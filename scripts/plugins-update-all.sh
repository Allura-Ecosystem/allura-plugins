#!/usr/bin/env bash
# Source-first catalog maintenance. Never installs plugins or edits runtime caches/config.
set -euo pipefail
CATALOG_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="check"
EXPLICIT_MODE=""
PACKAGES=()
EXPORT_ARGS=()
HAS_SOURCE=false
SOURCE_IDS=()

usage() {
  cat <<'HELP'
Usage: plugins-update-all.sh [--dry-run | --sync] [--package ID] [--source ID=PATH] [ID]

Default / --dry-run: read-only local catalog metadata, manifest and model audit.
With --source, also verify selected pinned exports against committed local sources.
In audit mode, source bindings select the exports when --package is omitted; every
selected export must have a local binding (no upstream network fetch).
--sync: regenerate selected pinned exports and catalog metadata inside this repository,
then validate. Local source commits must match source-locks.json and repository origin.
Without --source, explicit --sync may fetch the pinned source repositories.

--package ID       Source ID or compatibility alias; repeatable. Positional ID also works.
--source ID=PATH   Committed local source checkout; repeatable. Passed to pinned exporter.
--help            Show this help.

Package filters select source exports; metadata/manifest/model audits cover the catalog.
Without --source in audit mode, source content is NOT reverified against upstream.
This command never pulls installed marketplaces, clears caches, edits user configuration,
installs plugins, or restarts runtimes. Runtime installation flags are unsupported.
Local commits must be published separately before remote consumers can fetch their pins.
HELP
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --help|-h) usage; exit 0 ;;
    --dry-run|--sync)
      if [[ -n "$EXPLICIT_MODE" && "$EXPLICIT_MODE" != "$1" ]]; then
        echo "--dry-run and --sync are mutually exclusive" >&2; exit 2
      fi
      EXPLICIT_MODE="$1"
      [[ "$1" == "--sync" ]] && MODE="sync"
      shift ;;
    --package|--source)
      if [[ $# -lt 2 || -z "$2" || "$2" == --* ]]; then
        echo "$1 requires a value" >&2; exit 2
      fi
      if [[ "$1" == "--package" ]]; then PACKAGES+=("$2"); else
        [[ "$2" == *=?* ]] || { echo "--source requires ID=PATH" >&2; exit 2; }
        HAS_SOURCE=true; SOURCE_IDS+=("${2%%=*}")
      fi
      EXPORT_ARGS+=("$1" "$2")
      shift 2 ;;
    --package=*|--source=*)
      flag="${1%%=*}"; value="${1#*=}"
      if [[ -z "$value" ]]; then echo "$flag requires a value" >&2; exit 2; fi
      if [[ "$flag" == "--package" ]]; then PACKAGES+=("$value"); else
        [[ "$value" == *=?* ]] || { echo "--source requires ID=PATH" >&2; exit 2; }
        HAS_SOURCE=true; SOURCE_IDS+=("${value%%=*}")
      fi
      EXPORT_ARGS+=("$flag" "$value")
      shift ;;
    -*) echo "Unsupported option: $1. Runtime installation is not supported; use --help." >&2; exit 2 ;;
    *) PACKAGES+=("$1"); EXPORT_ARGS+=("--package" "$1"); shift ;;
  esac
done

if [[ "$MODE" == "check" ]] && $HAS_SOURCE && [[ ${#PACKAGES[@]} -eq 0 ]]; then
  for source_id in "${SOURCE_IDS[@]}"; do
    PACKAGES+=("$source_id"); EXPORT_ARGS+=("--package" "$source_id")
  done
fi

# Reject unknown selectors and prevent network fallback during a local source audit.
python3 - "$CATALOG_ROOT/source-locks.json" "$MODE" "${#SOURCE_IDS[@]}" "${SOURCE_IDS[@]}" "${PACKAGES[@]}" <<'PY'
import json
import sys
from pathlib import Path
try:
    locks = json.loads(Path(sys.argv[1]).read_text())["sources"]
    allowed = {name for lock in locks for name in [lock["id"], *lock.get("aliases", [])]}
    source_count = int(sys.argv[3])
    local_ids = set(sys.argv[4:4 + source_count])
    selectors = set(sys.argv[4 + source_count:])
    unknown = selectors - allowed
    if unknown:
        raise ValueError("unknown package selector(s): " + ", ".join(sorted(unknown)))
    if sys.argv[2] == "check" and local_ids:
        selected = {lock["id"] for lock in locks if selectors.intersection([lock["id"], *lock.get("aliases", [])])}
        if selected - local_ids:
            raise ValueError("audit requires --source for every selected export: " + ", ".join(sorted(selected - local_ids)))
except (OSError, ValueError, KeyError, TypeError) as exc:
    print(f"Catalog selection failed: {exc}", file=sys.stderr)
    raise SystemExit(2)
PY

if [[ "$MODE" == "sync" ]]; then
  python3 "$CATALOG_ROOT/scripts/verify_source_exports.py" --sync "${EXPORT_ARGS[@]}"
  python3 "$CATALOG_ROOT/scripts/sync_catalog_metadata.py"
elif $HAS_SOURCE; then
  python3 "$CATALOG_ROOT/scripts/verify_source_exports.py" --check "${EXPORT_ARGS[@]}"
fi

python3 "$CATALOG_ROOT/scripts/sync_catalog_metadata.py" --check
python3 "$CATALOG_ROOT/scripts/validate_manifests.py"
python3 "$CATALOG_ROOT/scripts/model-policy.py" audit

if [[ "$MODE" == "sync" ]]; then
  python3 "$CATALOG_ROOT/scripts/verify_source_exports.py" --check "${EXPORT_ARGS[@]}"
  echo "Pinned repository exports synchronized and audited. No plugins were installed or published."
elif $HAS_SOURCE; then
  echo "Local catalog and selected pinned exports verified. No changes made."
else
  echo "Local catalog audit passed. Pinned source content was not reverified; supply --source ID=PATH for that check. No changes made."
fi
