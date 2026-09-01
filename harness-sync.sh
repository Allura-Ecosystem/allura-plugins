#!/usr/bin/env bash
# Regenerate catalog packages from standalone repositories pinned in source-locks.json.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE=""
SELECTOR="all"
PROJECT=""

usage() {
  cat <<'USAGE'
Usage: ./harness-sync.sh --check|--sync [--team ALIAS] [--project ALIAS]

Modes:
  --check  Regenerate in temporary directories and fail on any byte/hash drift.
  --sync   Replace generated catalog destinations from pinned standalone sources.

Compatibility selectors:
  --team all|ram|team-ram|durham|team-durham|mortagate|mortgate
  --project team-ram-coding|team-ram-harness|team-durham|mortagate-cowork

The only direction is standalone canonical source @ pinned SHA -> generated catalog.
Project-overlay/catalog-as-canonical copying is intentionally unsupported.
USAGE
}

while (($#)); do
  case "$1" in
    --check|--sync)
      [[ -z "$MODE" ]] || { echo "choose exactly one of --check or --sync" >&2; exit 2; }
      MODE="$1"; shift ;;
    --team)
      [[ $# -ge 2 ]] || { echo "--team requires a value" >&2; exit 2; }
      SELECTOR="$2"; shift 2 ;;
    --team=*) SELECTOR="${1#*=}"; shift ;;
    --project)
      [[ $# -ge 2 ]] || { echo "--project requires a value" >&2; exit 2; }
      PROJECT="$2"; shift 2 ;;
    --project=*) PROJECT="${1#*=}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$MODE" ]] || { usage >&2; exit 2; }
if [[ -n "$PROJECT" ]]; then
  [[ "$SELECTOR" == "all" ]] || { echo "use --team or --project, not both" >&2; exit 2; }
  SELECTOR="$PROJECT"
fi

case "$SELECTOR" in
  all) PACKAGE_ARGS=() ;;
  ram|team-ram) PACKAGE_ARGS=(--package team-ram) ;;
  durham) PACKAGE_ARGS=(--package team-durham) ;;
  mortagate|mortgate) PACKAGE_ARGS=(--package mortagate-cowork) ;;
  team-ram-coding|team-ram-harness|team-durham|mortagate-cowork|mortgate-cowork)
    PACKAGE_ARGS=(--package "$SELECTOR") ;;
  *) echo "unknown source/package compatibility alias: $SELECTOR" >&2; exit 2 ;;
esac

exec python3 "$ROOT/scripts/verify_source_exports.py" "$MODE" "${PACKAGE_ARGS[@]}"
