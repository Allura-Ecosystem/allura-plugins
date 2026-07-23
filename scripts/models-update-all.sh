#!/usr/bin/env bash
# models-update-all.sh — sync agent frontmatter model: field to models.yaml registry
#
# Reads allura-plugins/docs/models.yaml as the single source of truth.
# For each agent, updates the model: frontmatter in the agent .md file
# to match the registry, using runtime-specific aliases.
#
# Usage:
#   bash allura-plugins/scripts/models-update-all.sh              # sync all
#   bash allura-plugins/scripts/models-update-all.sh --dry-run    # preview drift
#   bash allura-plugins/scripts/models-update-all.sh brooks       # one agent
#   bash allura-plugins/scripts/models-update-all.sh --runtime claude  # one runtime
#
# Exit 0 = success, Exit 1 = drift found or sync failed
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY="$REPO_ROOT/allura-plugins/docs/models.yaml"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

DRY_RUN=false
FILTER_AGENT=""
FILTER_RUNTIME=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --runtime) FILTER_RUNTIME="$2"; shift 2 ;;
    --runtime=*) FILTER_RUNTIME="${1#*=}"; shift ;;
    *) FILTER_AGENT="$1"; shift ;;
  esac
done

ANY_DRIFT=0
declare -a RESULTS

log() { echo "[models-update] $*" >&2; }

# ─── Agent file locations ────────────────────────────────────────────
# Maps plugin → runtime → agent dir
get_agent_dirs() {
  local plugin="$1"
  case "$plugin" in
    team-ram-harness)
      echo "claude:$REPO_ROOT/Agent-Harnesses/Allura-TeamRam/agents"
      echo "opencode:$REPO_ROOT/Agent-Harnesses/Allura-TeamRam/.opencode/agent/core"
      ;;
    team-durham)
      echo "claude:$REPO_ROOT/allura-plugins/team-durham/agents"
      ;;
    allura-cowork)
      echo "claude:$REPO_ROOT/allura-plugins/allura-cowork/agents"
      ;;
    team-ram-coding)
      echo "claude:$REPO_ROOT/allura-plugins/team-ram-coding/agents"
      ;;
  esac
}

# ─── Read registry with python (no yq dependency) ───────────────────
# Extracts agent → primary model mapping + model aliases
read_registry() {
  python3 << 'PYEOF'
import sys, yaml, os

registry_path = os.environ.get('REGISTRY_PATH', '')
with open(registry_path) as f:
    data = yaml.safe_load(f)

models = data.get('models', {})
agents = data.get('agents', {})

# Output: agent_name|primary_model_key|plugin
for agent_name, agent_data in agents.items():
    primary = agent_data.get('primary', '')
    plugin = agent_data.get('plugin', '')
    print(f"{agent_name}|{primary}|{plugin}")

# Output model aliases: model_key|runtime|alias
for model_key, model_data in models.items():
    aliases = model_data.get('aliases', {})
    for runtime, alias in aliases.items():
        print(f"ALIAS|{model_key}|{runtime}|{alias}")
PYEOF
}

export REGISTRY_PATH="$REGISTRY"

# ─── Get the alias for a model in a specific runtime ────────────────
get_alias() {
  local model_key="$1" runtime="$2"
  echo "$REGISTRY_DATA" | grep "^ALIAS|$model_key|$runtime|" | cut -d'|' -f4
}

# ─── Get primary model key for an agent ─────────────────────────────
get_primary() {
  local agent="$1"
  echo "$REGISTRY_DATA" | grep "^$agent|" | head -1 | cut -d'|' -f2
}

# ─── Get plugin for an agent ────────────────────────────────────────
get_plugin() {
  local agent="$1"
  echo "$REGISTRY_DATA" | grep "^$agent|" | head -1 | cut -d'|' -f3
}

# ─── Read current model from agent file frontmatter ────────────────
get_current_model() {
  local file="$1"
  python3 -c "
import re
with open('$file') as f:
    for line in f:
        if line.startswith('---'): continue
        m = re.match(r'^model:\s*(.+)$', line)
        if m:
            print(m.group(1).strip())
            break
        if line.strip() == '---': break
" 2>/dev/null
}

# ─── Update model in agent file frontmatter ────────────────────────
update_model() {
  local file="$1" new_model="$2"
  if $DRY_RUN; then
    log "DRY-RUN: would update $file → model: $new_model"
    return 0
  fi
  cp "$file" "${file}.bak-${TIMESTAMP}"
  python3 -c "
import re
with open('$file') as f:
    content = f.read()
# Replace model: line in frontmatter
new_content = re.sub(r'^(model:\s*).+$', r'\g<1>$new_model', content, count=1, flags=re.MULTILINE)
with open('$file', 'w') as f:
    f.write(new_content)
" 2>/dev/null
}

# ─── Main ───────────────────────────────────────────────────────────
log "Loading registry from $REGISTRY"
REGISTRY_DATA=$(read_registry)

log "Scanning agents for model drift..."
$DRY_RUN && log "DRY-RUN mode — no writes"

# Get all agents from registry
AGENTS=$(echo "$REGISTRY_DATA" | grep -v "^ALIAS|" | cut -d'|' -f1)

for agent in $AGENTS; do
  # Apply agent filter
  if [[ -n "$FILTER_AGENT" && "$agent" != "$FILTER_AGENT" ]]; then continue; fi

  primary_key=$(get_primary "$agent")
  plugin=$(get_plugin "$agent")

  # Get agent dirs for this plugin
  agent_dirs=$(get_agent_dirs "$plugin")

  while IFS=':' read -r runtime dir; do
    [[ -z "$runtime" || -z "$dir" ]] && continue
    # Apply runtime filter
    if [[ -n "$FILTER_RUNTIME" && "$runtime" != "$FILTER_RUNTIME" ]]; then continue; fi

    agent_file="$dir/$agent.md"
    if [[ ! -f "$agent_file" ]]; then
      continue
    fi

    # Get the alias for this runtime
    expected_model=$(get_alias "$primary_key" "$runtime")
    if [[ -z "$expected_model" ]]; then
      # No alias for this runtime — use inherit or skip
      if [[ "$runtime" == "codex" ]]; then
        expected_model="inherit"
      elif [[ "$runtime" == "hermes" ]]; then
        expected_model="auto"
      else
        continue
      fi
    fi

    current_model=$(get_current_model "$agent_file")

    if [[ "$current_model" == "$expected_model" ]]; then
      status="up-to-date"
    else
      status="DRIFT"
      ANY_DRIFT=1
      update_model "$agent_file" "$expected_model"
    fi

    RESULTS+=("$agent|$runtime|$current_model|$expected_model|$status")
  done <<< "$agent_dirs"
done

# Print summary table
echo ""
echo "AGENT               RUNTIME  CURRENT                     EXPECTED                    STATUS"
echo "─────────────────── ──────── ──────────────────────────── ──────────────────────────── ──────────"
for row in "${RESULTS[@]}"; do
  IFS='|' read -r agent runtime current expected status <<< "$row"
  printf "%-19s %-8s %-28s %-28s %s\n" "$agent" "$runtime" "$current" "$expected" "$status"
done

echo ""
if $DRY_RUN; then
  if [[ $ANY_DRIFT -eq 0 ]]; then
    log "✅ No drift found — all agents match registry"
  else
    log "❌ Drift found — run without --dry-run to sync"
  fi
else
  log "Sync complete. Backups saved with .bak-$TIMESTAMP suffix."
fi

exit $ANY_DRIFT