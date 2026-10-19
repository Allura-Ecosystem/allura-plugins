#!/usr/bin/env bash
# Read-only catalog policy tool. Use --help for selectors and --dry-run for a plan.
# No source, generated export, installed cache, or global runtime configuration is changed.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/model-policy.py" eval "$@"
