#!/usr/bin/env bash
# plugins-update-all.sh — unified plugin update across 4 runtimes (Claude, Codex, Hermes, OpenClaw)
# Usage:
#   bash allura-plugins/scripts/plugins-update-all.sh              # update all
#   bash allura-plugins/scripts/plugins-update-all.sh --dry-run    # preview only
#   bash allura-plugins/scripts/plugins-update-all.sh team-durham  # one plugin
#   bash allura-plugins/scripts/plugins-update-all.sh --runtime hermes  # one runtime
# Exit 0 = success, Exit 1 = any plugin failed
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ALLURA_PLUGINS="$REPO_ROOT/allura-plugins"
TEAM_RAM="$REPO_ROOT/Agent-Harnesses/Allura-TeamRam"
CLAUDE_PLUGINS_DIR="$HOME/.claude/plugins"
CLAUDE_CACHE="$CLAUDE_PLUGINS_DIR/cache"
CLAUDE_MARKETPLACES="$CLAUDE_PLUGINS_DIR/marketplaces"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"

DRY_RUN=false
FILTER_PLUGIN=""
FILTER_RUNTIME=""

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --runtime) FILTER_RUNTIME="$2"; shift 2 ;;
    --runtime=*) FILTER_RUNTIME="${1#*=}"; shift ;;
    *) FILTER_PLUGIN="$1"; shift ;;
  esac
done

# State
declare -a RESULTS
ANY_FAIL=0

log() { echo "[plugins-update] $*" >&2; }

# Read a JSON field safely (python3 required)
json_get() {
  local file="$1" field="$2"
  python3 -c "import json; d=json.load(open('$file')); print(d.get('$field',''))" 2>/dev/null
}

# Read a YAML top-level field (simple key: value)
yaml_get() {
  local file="$1" field="$2"
  python3 -c "
import re
with open('$file') as f:
    for line in f:
        m=re.match(r'^${field}:\s*\"?([^\"\n#]+)\"?\s*(?:#.*)?$', line.strip())
        if m:
            print(m.group(1))
            break
" 2>/dev/null
}

# Sync a version into a Claude marketplace.json (match by plugin name)
sync_claude_marketplace() {
  local mp_file="$1" plugin_name="$2" new_version="$3"
  if [[ ! -f "$mp_file" ]]; then return 0; fi
  if $DRY_RUN; then
    log "DRY-RUN: would sync $plugin_name v$new_version into $mp_file"
    return 0
  fi
  cp "$mp_file" "${mp_file}.bak-${TIMESTAMP}"
  python3 -c "
import json
with open('$mp_file') as f:
    d = json.load(f)
changed = False
for p in d.get('plugins', []):
    if p.get('name') == '$plugin_name':
        if p.get('version') != '$new_version':
            p['version'] = '$new_version'
            changed = True
if d.get('metadata',{}).get('version') and '$plugin_name' == 'team-ram-harness':
    if d['metadata']['version'] != '$new_version':
        d['metadata']['version'] = '$new_version'
        changed = True
if changed:
    with open('$mp_file', 'w') as f:
        json.dump(d, f, indent=2)
    print('synced')
else:
    print('no-change')
" 2>/dev/null
}

# Clear Claude cache for a specific plugin version
clear_claude_cache() {
  local marketplace="$1" plugin="$2" version="$3"
  local cache_dir="$CLAUDE_CACHE/$marketplace/$plugin/$version"
  if [[ -d "$cache_dir" ]]; then
    if $DRY_RUN; then
      log "DRY-RUN: would rm -rf $cache_dir"
    else
      rm -rf "$cache_dir"
      log "cleared cache: $cache_dir"
    fi
  fi
}

# Git pull a marketplace (for git-source marketplaces)
git_pull_marketplace() {
  local mp_name="$1"
  local mp_dir="$CLAUDE_MARKETPLACES/$mp_name"
  if [[ -d "$mp_dir/.git" ]]; then
    if $DRY_RUN; then
      log "DRY-RUN: would git pull in $mp_dir"
    else
      (cd "$mp_dir" && git pull --ff-only 2>&1 | head -3) || log "WARN: git pull failed in $mp_dir"
    fi
  fi
}

# Add a result row
add_result() {
  local plugin="$1" runtime="$2" old_v="$3" new_v="$4" marketplace="$5" status="$6"
  # Apply filters
  if [[ -n "$FILTER_PLUGIN" && "$plugin" != "$FILTER_PLUGIN" ]]; then return; fi
  if [[ -n "$FILTER_RUNTIME" && "$runtime" != "$(echo "$FILTER_RUNTIME" | sed 's/.*/\u&/')" ]]; then return; fi
  RESULTS+=("$plugin|$runtime|$old_v|$new_v|$marketplace|$status")
  if [[ "$status" == "failed" ]]; then ANY_FAIL=1; fi
}

# ─── Scan Claude plugins ─────────────────────────────────────────────
scan_claude() {
  local runtime="Claude"
  # allura-ecosystem marketplace plugins
  local mp_file="$ALLURA_PLUGINS/.claude-plugin/marketplace.json"
  if [[ -f "$mp_file" ]]; then
    while IFS='|' read -r name source version; do
      local plugin_dir
      if [[ "$source" == ./* ]]; then
        plugin_dir="$ALLURA_PLUGINS/${source#./}"
      elif [[ "$source" == ../* ]]; then
        plugin_dir="$REPO_ROOT/${source#../}"
      else
        plugin_dir="$source"
      fi
      local pj="$plugin_dir/.claude-plugin/plugin.json"
      if [[ -f "$pj" ]]; then
        local current_v
        current_v=$(json_get "$pj" "version")
        if [[ -z "$current_v" ]]; then current_v="$version"; fi
        local status="up-to-date"
        if [[ "$current_v" != "$version" ]]; then status="updated"; fi
        sync_claude_marketplace "$mp_file" "$name" "$current_v"
        if [[ "$status" == "updated" ]]; then clear_claude_marketplace_cache "$name" "$version"; fi
        add_result "$name" "$runtime" "$version" "$current_v" "allura-ecosystem" "$status"
      fi
    done < <(python3 -c "
import json
with open('$mp_file') as f:
    d = json.load(f)
for p in d.get('plugins', []):
    print(f\"{p.get('name','')}|{p.get('source','')}|{p.get('version','')}\")
" 2>/dev/null)
  fi

  # team-ram-harness (separate marketplace)
  local tr_mp="$TEAM_RAM/.claude-plugin/marketplace.json"
  local tr_pj="$TEAM_RAM/.claude-plugin/plugin.json"
  if [[ -f "$tr_mp" && -f "$tr_pj" ]]; then
    local tr_name tr_current_v tr_mp_v
    tr_name=$(json_get "$tr_pj" "name")
    tr_current_v=$(json_get "$tr_pj" "version")
    tr_mp_v=$(json_get "$tr_mp" "metadata.version")
    local status="up-to-date"
    if [[ "$tr_current_v" != "$tr_mp_v" ]]; then status="updated"; fi
    sync_claude_marketplace "$tr_mp" "$tr_name" "$tr_current_v"
    if [[ "$status" == "updated" ]]; then clear_claude_cache "team-ram-marketplace" "$tr_name" "$tr_mp_v"; fi
    add_result "$tr_name" "$runtime" "$tr_mp_v" "$tr_current_v" "team-ram-marketplace" "$status"
  fi
}

clear_claude_marketplace_cache() {
  local plugin="$1" old_version="$2"
  # Try common marketplace dirs
  for mp in allura-ecosystem team-ram-marketplace; do
    clear_claude_cache "$mp" "$plugin" "$old_version"
  done
}

# ─── Scan Codex plugins ─────────────────────────────────────────────
scan_codex() {
  local runtime="Codex"
  for dir in "$ALLURA_PLUGINS"/*/; do
    local name
    name=$(basename "$dir")
    local pj="$dir.codex-plugin/plugin.json"
    if [[ -f "$pj" ]]; then
      local version
      version=$(json_get "$pj" "version")
      if [[ -n "$version" ]]; then
        add_result "$name" "$runtime" "$version" "$version" "config.toml" "up-to-date"
      fi
    fi
  done
  # team-ram-harness codex
  local tr_pj="$TEAM_RAM/.codex-plugin/plugin.json"
  if [[ -f "$tr_pj" ]]; then
    local name version
    name=$(json_get "$tr_pj" "name")
    version=$(json_get "$tr_pj" "version")
    add_result "$name" "$runtime" "$version" "$version" "config.toml" "up-to-date"
  fi
}

# ─── Scan Hermes plugins ─────────────────────────────────────────────
scan_hermes() {
  local runtime="Hermes"
  # Check both locations: allura-plugins/plugins/*/ and allura-plugins/*/
  for dir in "$ALLURA_PLUGINS"/plugins/*/ "$ALLURA_PLUGINS"/*/; do
    [[ -d "$dir" ]] || continue
    local yaml="$dir/plugin.yaml"
    if [[ -f "$yaml" ]]; then
      local name version
      name=$(yaml_get "$yaml" "name")
      version=$(yaml_get "$yaml" "version")
      if [[ -n "$name" && -n "$version" ]]; then
        local status="up-to-date"
        # Try hermes plugins update if CLI available and not dry-run
        if command -v hermes &>/dev/null; then
          if ! $DRY_RUN; then
            if hermes plugins update "$name" 2>/dev/null; then
              status="updated"
            fi
            # Post-update verification for allura-brain
            if [[ "$name" == "allura-brain" ]]; then
              hermes allura-brain status 2>/dev/null || log "WARN: hermes allura-brain status failed"
            fi
          else
            log "DRY-RUN: would run 'hermes plugins update $name'"
          fi
        else
          status="cli-missing"
          if ! $DRY_RUN; then log "WARN: hermes CLI not found — manual update: cd $dir, git pull"; fi
        fi
        add_result "$name" "$runtime" "$version" "$version" "git" "$status"
      fi
    fi
  done
}

# ─── Scan OpenClaw plugins ──────────────────────────────────────────
scan_openclaw() {
  local runtime="OpenClaw"
  # Check for native openclaw.plugin.json in allura-plugins
  for dir in "$ALLURA_PLUGINS"/*/; do
    local name
    name=$(basename "$dir")
    local oj="$dir/openclaw.plugin.json"
    if [[ -f "$oj" ]]; then
      local version
      version=$(json_get "$oj" "version")
      if [[ -n "$version" ]]; then
        local status="up-to-date"
        if command -v openclaw &>/dev/null; then
          if ! $DRY_RUN; then
            if openclaw plugins update "$name" 2>/dev/null; then
              status="updated"
              openclaw gateway restart 2>/dev/null || log "WARN: openclaw gateway restart failed"
            fi
          else
            log "DRY-RUN: would run 'openclaw plugins update $name' + gateway restart"
          fi
        else
          status="cli-missing"
        fi
        add_result "$name" "$runtime" "$version" "$version" "clawhub/npm" "$status"
      fi
    fi
  done
  # Note: no Allura OpenClaw plugins exist yet — report compatible-bundle option
  if [[ -z "$FILTER_PLUGIN" && -z "$FILTER_RUNTIME" ]]; then
    add_result "(none yet)" "$runtime" "-" "-" "compatible-bundle" "not-installed"
  fi
}

# ─── Git pull git-source marketplaces ───────────────────────────────
update_git_marketplaces() {
  if $DRY_RUN; then
    log "DRY-RUN: would git pull git-source marketplaces"
    return
  fi
  for mp_name in team-durham-local allura-local claude-plugins-official superpowers-dev harness-marketplace; do
    git_pull_marketplace "$mp_name"
  done
}

# ─── Main ───────────────────────────────────────────────────────────
log "Scanning Allura plugins across 4 runtimes..."
$DRY_RUN && log "DRY-RUN mode — no writes, no update commands, no cache clearing"

scan_claude
scan_codex
scan_hermes
scan_openclaw
update_git_marketplaces

# Print summary table
echo ""
echo "PLUGIN              RUNTIME  OLD     NEW     MARKETPLACE           STATUS"
echo "─────────────────── ──────── ─────── ─────── ───────────────────── ─────────────"
for row in "${RESULTS[@]}"; do
  IFS='|' read -r plugin runtime old_v new_v marketplace status <<< "$row"
  printf "%-19s %-8s %-7s %-7s %-21s %s\n" "$plugin" "$runtime" "$old_v" "$new_v" "$marketplace" "$status"
done

echo ""
if $DRY_RUN; then
  log "Dry run complete. No changes made."
else
  log "Update complete. Restart Claude/Codex to load updated plugins."
fi

exit $ANY_FAIL