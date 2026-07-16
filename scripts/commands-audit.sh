#!/usr/bin/env bash
# commands-audit.sh — audit plugin commands for orphans, collisions, and missing frontmatter
# Usage: bash allura-plugins/scripts/commands-audit.sh
# Exit 0 = clean, Exit 1 = issues found
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ANY_FAIL=0

log() { echo "[commands-audit] $*" >&2; }

# Plugin definitions: name|commands_dir|claude_manifest|codex_manifest
PLUGINS=(
  "team-ram-harness|$REPO_ROOT/Agent-Harnesses/Allura-TeamRam/.opencode/command|$REPO_ROOT/Agent-Harnesses/Allura-TeamRam/.claude-plugin/plugin.json|$REPO_ROOT/Agent-Harnesses/Allura-TeamRam/.codex-plugin/plugin.json"
  "team-durham|$REPO_ROOT/allura-plugins/team-durham/commands|$REPO_ROOT/allura-plugins/team-durham/.claude-plugin/plugin.json|$REPO_ROOT/allura-plugins/team-durham/.codex-plugin/plugin.json"
  "allura-cowork|$REPO_ROOT/allura-plugins/allura-cowork/commands|$REPO_ROOT/allura-plugins/allura-cowork/.claude-plugin/plugin.json|$REPO_ROOT/allura-plugins/allura-cowork/.codex-plugin/plugin.json"
  "team-ram-coding|$REPO_ROOT/allura-plugins/team-ram-coding/commands|$REPO_ROOT/allura-plugins/team-ram-coding/.claude-plugin/plugin.json|$REPO_ROOT/allura-plugins/team-ram-coding/.codex-plugin/plugin.json"
)

echo "PLUGIN COMMAND AUDIT"
echo "═══════════════════════════════════════════════════════════════════════════"

# ─── Check 1: Orphan commands (on disk but not in manifest) ──────────
echo ""
echo "CHECK 1: Orphan commands (on disk, not registered in manifest)"
echo "─────────────────────────────────────────────────────────────"

ORPHAN_COUNT=0
for entry in "${PLUGINS[@]}"; do
  IFS='|' read -r name cmd_dir claude_mf codex_mf <<< "$entry"
  [[ -d "$cmd_dir" ]] || continue

  # Get on-disk commands
  declare -a on_disk=()
  for f in "$cmd_dir"/*.md; do
    [[ -f "$f" ]] && on_disk+=("$(basename "$f")")
  done

  # Get registered commands from Claude manifest
  declare -a registered=()
  if [[ -f "$claude_mf" ]]; then
    while IFS= read -r line; do
      registered+=("$line")
    done < <(python3 -c "
import json
d = json.load(open('$claude_mf'))
cmds = d.get('commands', [])
if isinstance(cmds, list):
    for c in cmds:
        print(c.split('/')[-1])
" 2>/dev/null)
  fi

  # Find orphans
  for f in "${on_disk[@]}"; do
    found=false
    for r in "${registered[@]}"; do
      if [[ "$f" == "$r" ]]; then found=true; break; fi
    done
    if ! $found; then
      echo "  ORPHAN: $name → $f (not in Claude manifest)"
      ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
      ANY_FAIL=1
    fi
  done
done
[[ $ORPHAN_COUNT -eq 0 ]] && echo "  ✅ No orphans found"

# ─── Check 2: Manifest format consistency ────────────────────────────
echo ""
echo "CHECK 2: Manifest format (array vs glob vs missing)"
echo "──────────────────────────────────────────────────"

for entry in "${PLUGINS[@]}"; do
  IFS='|' read -r name cmd_dir claude_mf codex_mf <<< "$entry"
  for mf_label in "Claude:$claude_mf" "Codex:$codex_mf"; do
    IFS=':' read -r label mf <<< "$mf_label"
    [[ -f "$mf" ]] || continue
    fmt=$(python3 -c "
import json
d = json.load(open('$mf'))
cmds = d.get('commands', 'NOT_SET')
if isinstance(cmds, list): print(f'array ({len(cmds)})')
elif isinstance(cmds, str): print(f'glob: \"{cmds}\"')
else: print('NOT_SET')
" 2>/dev/null)
    if [[ "$fmt" == "NOT_SET" ]]; then
      echo "  ⚠️  $name ($label): commands not set"
    elif [[ "$fmt" == glob* ]]; then
      echo "  ⚠️  $name ($label): $fmt — should be explicit array"
      ANY_FAIL=1
    else
      echo "  ✅ $name ($label): $fmt"
    fi
  done
done

# ─── Check 3: Missing description frontmatter ────────────────────────
echo ""
echo "CHECK 3: Commands missing 'description:' frontmatter"
echo "──────────────────────────────────────────────────────"

MISSING_DESC=0
for entry in "${PLUGINS[@]}"; do
  IFS='|' read -r name cmd_dir claude_mf codex_mf <<< "$entry"
  [[ -d "$cmd_dir" ]] || continue
  for f in "$cmd_dir"/*.md; do
    [[ -f "$f" ]] || continue
    if ! head -10 "$f" | grep -q "^description:"; then
      echo "  MISSING: $name/$(basename "$f")"
      MISSING_DESC=$((MISSING_DESC + 1))
      ANY_FAIL=1
    fi
  done
done
[[ $MISSING_DESC -eq 0 ]] && echo "  ✅ All commands have description frontmatter"

# ─── Check 4: Cross-plugin name collisions ───────────────────────────
echo ""
echo "CHECK 4: Cross-plugin command name collisions"
echo "──────────────────────────────────────────────"

declare -A cmd_plugins
for entry in "${PLUGINS[@]}"; do
  IFS='|' read -r name cmd_dir claude_mf codex_mf <<< "$entry"
  [[ -d "$cmd_dir" ]] || continue
  for f in "$cmd_dir"/*.md; do
    [[ -f "$f" ]] || continue
    base=$(basename "$f" .md)
    cmd_plugins["$base"]+="$name,"
  done
done

COLLISION_COUNT=0
for cmd in "${!cmd_plugins[@]}"; do
  plugins="${cmd_plugins[$cmd]}"
  # Count plugins (comma-separated)
  count=$(echo "$plugins" | tr ',' '\n' | grep -c .)
  if [[ $count -gt 1 ]]; then
    echo "  COLLISION: /$cmd in: $(echo "$plugins" | tr ',' ' ')"
    COLLISION_COUNT=$((COLLISION_COUNT + 1))
  fi
done
[[ $COLLISION_COUNT -eq 0 ]] && echo "  ✅ No collisions" || echo "  ($COLLISION_COUNT collisions — document or namespace if plugins co-installed)"

# ─── Summary ─────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "SUMMARY: orphans=$ORPHAN_COUNT, missing-desc=$MISSING_DESC, collisions=$COLLISION_COUNT"
if [[ $ANY_FAIL -eq 0 ]]; then
  echo "✅ All checks pass"
  exit 0
else
  echo "❌ Issues found — see above"
  exit 1
fi