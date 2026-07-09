#!/usr/bin/env bash
###############################################################################
# harness-sync.sh — Allura Harness Drift Detection & Sync
#
# Identifies "core" harness files (agents, commands, plugin manifest) that
# should be identical across all project copies of a team's harness, compares
# each project against the canonical source, and reports or repairs drift.
#
# Usage:
#   harness-sync.sh --check                          # check all teams, all projects
#   harness-sync.sh --check --team ram               # check RAM projects only
#   harness-sync.sh --check --team durham            # check Durham projects only
#   harness-sync.sh --check --team ram --project allura-cowork  # check one project
#   harness-sync.sh --sync                           # sync all teams, all projects
#   harness-sync.sh --sync --team ram                # sync RAM projects only
#   harness-sync.sh --sync --team ram --project allura-cowork   # sync one project
#
# Exit codes:
#   0 — no drift (or sync completed successfully)
#   1 — drift found (in --check mode)
#   2 — usage error / missing dependencies
#
# Core files (checked for drift):
#   agents/*.md              — agent personas
#   commands/**/*.md         — slash commands (including subdirs like openagents/)
#   .codex-plugin/plugin.json — plugin manifest
#
# Overlay files (NOT checked — per-project customization):
#   skills/**                — per-project skill packs
#   config/**                — per-project configuration
#   scripts/**               — per-project scripts
#   hooks/**                 — per-project hooks
#   assets/**                — per-project assets
#   .claude-plugin/**        — Claude-specific manifest
#   README.md                — per-project readme
#   Any other file           — treated as project-specific overlay
###############################################################################

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PLUGINS_DIR="${PLUGINS_DIR:-$HOME/plugins}"

# --- Team → Canonical source mapping --------------------------------------
RAM_CANONICAL="team-ram-coding"
DURHAM_CANONICAL="team-durham"

# --- Team → Project copies (excluding canonical) --------------------------
# These are plugin directories that share the team's core harness.
# Add new project plugins here as they are created.
RAM_PROJECTS=("team-ram-payload" "allura-cowork" "allura")
DURHAM_PROJECTS=()  # No Durham project copies yet — add as they appear

# --- Core file patterns (relative to plugin root) -------------------------
# These are the files that MUST be identical across canonical and all projects.
# Uses find-style patterns relative to the plugin root directory.
CORE_FIND_EXPR=(
    -type f
    \( -path "agents/*.md" \)
    -o \( -path "commands/*.md" \)
    -o \( -path "commands/*/*.md" \)
    -o -path ".codex-plugin/plugin.json"
)

# --- Overlay patterns (explicitly NOT checked) -----------------------------
# Listed for documentation purposes; the script simply ignores anything
# not matching CORE_FIND_EXPR.
OVERLAY_PATTERNS=(
    "skills/**"
    "config/**"
    "scripts/**"
    "hooks/**"
    "assets/**"
    ".claude-plugin/**"
    "README.md"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Color codes (disabled if not a TTY)
if [[ -t 1 ]]; then
    C_RED='\033[0;31m'
    C_GREEN='\033[0;32m'
    C_YELLOW='\033[0;33m'
    C_CYAN='\033[0;36m'
    C_BOLD='\033[1m'
    C_DIM='\033[2m'
    C_RESET='\033[0m'
else
    C_RED='' C_GREEN='' C_YELLOW='' C_CYAN='' C_BOLD='' C_DIM='' C_RESET=''
fi

log_info()  { printf "${C_CYAN}[INFO]${C_RESET}  %s\n" "$*" >&2; }
log_ok()    { printf "${C_GREEN}[OK]${C_RESET}    %s\n" "$*" >&2; }
log_warn()  { printf "${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*" >&2; }
log_error() { printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" >&2; }

die() {
    log_error "$@"
    exit 2
}

# Print a formatted table row (pipe-delimited, then we format it)
# Usage: print_table_header
print_table_header() {
    printf "\n"
    printf "${C_BOLD}%-45s  %-10s  %-8s  %-8s  %s${C_RESET}\n" \
        "FILE" "STATUS" "CANON" "PROJ" "DETAILS"
    printf '%.0s─' {1..100}
    printf "\n"
}

print_table_row() {
    local file="$1" status="$2" canon_size="$3" proj_size="$4" details="$5"
    local status_colored

    case "$status" in
        OK)      status_colored="${C_GREEN}${status}${C_RESET}" ;;
        DRIFT)   status_colored="${C_RED}${status}${C_RESET}" ;;
        MISSING) status_colored="${C_YELLOW}${status}${C_RESET}" ;;
        *)       status_colored="$status" ;;
    esac

    # Strip color codes for width calculation
    local plain_status="$status"
    printf "%-45s  %-10s  %-8s  %-8s  %s\n" \
        "$file" "$plain_status" "$canon_size" "$proj_size" "$details"
}

# Enumerate core files in a plugin directory (relative paths, sorted)
# Usage: enumerate_core_files /path/to/plugin
enumerate_core_files() {
    local plugin_dir="$1"
    [[ -d "$plugin_dir" ]] || return 0

    # Use find with the core patterns, output relative paths
    # We cd into the plugin dir so find outputs relative paths
    (
        cd "$plugin_dir" 2>/dev/null || exit 0
        find . \
            -not -path './.git/*' \
            -type f \
            \( \
                -path './agents/*.md' \
                -o -path './commands/*.md' \
                -o -path './commands/*/*.md' \
                -o -path './.codex-plugin/plugin.json' \
            \) \
            -printf '%P\n' 2>/dev/null
    ) | sort
}

# Compute a quick checksum + size for a file
# Returns: "size:checksum"
file_fingerprint() {
    local f="$1"
    if [[ ! -f "$f" ]]; then
        echo "-:MISSING"
        return
    fi
    local size checksum
    size=$(wc -c < "$f" | tr -d ' ')
    checksum=$(md5sum "$f" | cut -d' ' -f1)
    echo "${size}:${checksum}"
}

# ---------------------------------------------------------------------------
# Core logic: compare one project against its canonical source
# ---------------------------------------------------------------------------

# Returns 0 if no drift, 1 if drift found
# Sets global: DRIFT_COUNT, MISSING_COUNT, OK_COUNT
check_project() {
    local canonical_dir="$1"
    local project_dir="$2"
    local project_name="$3"
    local team_name="$4"

    local drift_count=0
    local missing_count=0
    local ok_count=0
    local has_drift=0

    # Get core file lists from both canonical and project
    local -a canonical_files project_files
    mapfile -t canonical_files < <(enumerate_core_files "$canonical_dir")
    mapfile -t project_files < <(enumerate_core_files "$project_dir")

    # Build a set of all core files (union, sorted)
    local -a all_files
    mapfile -t all_files < <(printf '%s\n' "${canonical_files[@]}" "${project_files[@]}" 2>/dev/null | sort -u)

    # Filter: only files that are in canonical are "core" — files only in project
    # are project-specific additions (overlay agents/commands), not core drift.
    # However, if a core file from canonical is MISSING from project, that's drift.

    printf "\n${C_BOLD}=== Team: %s | Project: %s ===${C_RESET}\n" "$team_name" "$project_name"
    printf "${C_DIM}Canonical: %s${C_RESET}\n" "$canonical_dir"
    printf "${C_DIM}Project:   %s${C_RESET}\n" "$project_dir"

    if [[ ${#all_files[@]} -eq 0 ]] && [[ ${#canonical_files[@]} -eq 0 ]]; then
        printf "  ${C_DIM}(no core files in canonical — skipping)${C_RESET}\n"
        DRIFT_COUNT=0; MISSING_COUNT=0; OK_COUNT=0
        return 0
    fi

    print_table_header

    for f in "${canonical_files[@]}"; do
        [[ -z "$f" ]] && continue

        local canon_path="${canonical_dir}/${f}"
        local proj_path="${project_dir}/${f}"

        local canon_fp proj_fp
        canon_fp=$(file_fingerprint "$canon_path")
        proj_fp=$(file_fingerprint "$proj_path")

        local canon_size="${canon_fp%%:*}"
        local canon_hash="${canon_fp#*:}"
        local proj_size="${proj_fp%%:*}"
        local proj_hash="${proj_fp#*:}"

        if [[ "$proj_hash" == "MISSING" ]]; then
            print_table_row "$f" "MISSING" "$canon_size" "-" "file not found in project"
            ((missing_count++))
            has_drift=1
        elif [[ "$canon_hash" != "$proj_hash" ]]; then
            local detail=""
            if [[ "$canon_size" != "$proj_size" ]]; then
                detail="size differs (${canon_size} vs ${proj_size} bytes)"
            else
                detail="content differs (same size, different checksum)"
            fi
            print_table_row "$f" "DRIFT" "$canon_size" "$proj_size" "$detail"
            ((drift_count++))
            has_drift=1
        else
            print_table_row "$f" "OK" "$canon_size" "$proj_size" "identical"
            ((ok_count++))
        fi
    done

    # Check for project-only core files (extra agents/commands not in canonical)
    local -A canonical_set
    for f in "${canonical_files[@]}"; do
        canonical_set["$f"]=1
    done

    local extra_count=0
    for f in "${project_files[@]}"; do
        [[ -z "$f" ]] && continue
        if [[ -z "${canonical_set[$f]:-}" ]]; then
            local proj_path="${project_dir}/${f}"
            local proj_fp proj_size
            proj_fp=$(file_fingerprint "$proj_path")
            proj_size="${proj_fp%%:*}"
            print_table_row "$f" "EXTRA" "-" "$proj_size" "project-only (overlay — not drift)"
            ((extra_count++))
        fi
    done

    # Summary
    printf "\n"
    printf "  ${C_BOLD}Summary:${C_RESET}  %d OK  |  %d drift  |  %d missing  |  %d project-only\n" \
        "$ok_count" "$drift_count" "$missing_count" "$extra_count"

    if [[ $has_drift -eq 1 ]]; then
        printf "  ${C_RED}${C_BOLD}*** CORE DRIFT FOUND ***${C_RESET}\n"
    else
        printf "  ${C_GREEN}${C_BOLD}*** NO DRIFT ***${C_RESET}\n"
    fi

    DRIFT_COUNT="$drift_count"
    MISSING_COUNT="$missing_count"
    OK_COUNT="$ok_count"
    return $has_drift
}

# Sync core files from canonical to a project
sync_project() {
    local canonical_dir="$1"
    local project_dir="$2"
    local project_name="$3"
    local team_name="$4"

    local synced_count=0
    local created_count=0

    printf "\n${C_BOLD}=== SYNC: Team %s → Project %s ===${C_RESET}\n" "$team_name" "$project_name"

    # Get core files from canonical
    local -a canonical_files
    mapfile -t canonical_files < <(enumerate_core_files "$canonical_dir")

    if [[ ${#canonical_files[@]} -eq 0 ]]; then
        printf "  ${C_DIM}(no core files in canonical — nothing to sync)${C_RESET}\n"
        return 0
    fi

    print_table_header

    for f in "${canonical_files[@]}"; do
        [[ -z "$f" ]] && continue

        local canon_path="${canonical_dir}/${f}"
        local proj_path="${project_dir}/${f}"
        local proj_dir
        proj_dir=$(dirname "$proj_path")

        local canon_fp proj_fp
        canon_fp=$(file_fingerprint "$canon_path")
        proj_fp=$(file_fingerprint "$proj_path")

        local canon_size="${canon_fp%%:*}"
        local proj_size="${proj_fp%%:*}"

        if [[ "$proj_fp" == "-:MISSING" ]]; then
            # Create directory and copy
            mkdir -p "$proj_dir"
            cp "$canon_path" "$proj_path"
            print_table_row "$f" "CREATED" "$canon_size" "$canon_size" "copied from canonical"
            ((created_count++))
            ((synced_count++))
        elif [[ "$canon_fp" != "$proj_fp" ]]; then
            # File differs — copy
            cp "$canon_path" "$proj_path"
            local detail=""
            if [[ "$canon_size" != "$proj_size" ]]; then
                detail="overwritten (was ${proj_size} bytes)"
            else
                detail="overwritten (content differed, same size)"
            fi
            print_table_row "$f" "SYNCED" "$canon_size" "$canon_size" "$detail"
            ((synced_count++))
        else
            print_table_row "$f" "OK" "$canon_size" "$proj_size" "already in sync"
        fi
    done

    printf "\n"
    printf "  ${C_BOLD}Sync complete:${C_RESET}  %d files synced  |  %d created  |  %d already in sync\n" \
        "$synced_count" "$created_count" "$((${#canonical_files[@]} - synced_count))"

    return 0
}

# ---------------------------------------------------------------------------
# Team orchestration
# ---------------------------------------------------------------------------

# Get canonical dir for a team
get_canonical() {
    local team="$1"
    case "$team" in
        ram)    echo "${PLUGINS_DIR}/${RAM_CANONICAL}" ;;
        durham) echo "${PLUGINS_DIR}/${DURHAM_CANONICAL}" ;;
        *)      return 1 ;;
    esac
}

# Get project list for a team (as array)
get_projects() {
    local team="$1"
    case "$team" in
        ram)    printf '%s\n' "${RAM_PROJECTS[@]}" ;;
        durham) printf '%s\n' "${DURHAM_PROJECTS[@]}" ;;
        *)      return 1 ;;
    esac
}

# Get team display name
get_team_display() {
    local team="$1"
    case "$team" in
        ram)    echo "RAM" ;;
        durham) echo "Durham" ;;
        *)      echo "$team" ;;
    esac
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

MODE=""
TEAM=""
PROJECT=""

usage() {
    cat <<'USAGE'
harness-sync.sh — Allura Harness Drift Detection & Sync

USAGE:
  harness-sync.sh --check [OPTIONS]
  harness-sync.sh --sync  [OPTIONS]

MODES (exactly one required):
  --check     Compare core files and report drift. Exits 1 if drift found.
  --sync      Copy core files from canonical source to all project copies.

OPTIONS:
  --team TEAM       Team to check: ram, durham, or all (default: all)
  --project NAME    Specific project plugin to check (default: all projects)
  --plugins-dir DIR Override plugins directory (default: $HOME/plugins)
  -h, --help        Show this help message

EXAMPLES:
  # Check all teams, all projects (CI mode)
  harness-sync.sh --check

  # Check only RAM projects
  harness-sync.sh --check --team ram

  # Check one specific project
  harness-sync.sh --check --team ram --project allura-cowork

  # Sync all teams
  harness-sync.sh --sync

  # Sync one project
  harness-sync.sh --sync --team ram --project team-ram-payload

CORE FILES (checked for drift):
  agents/*.md              Agent persona definitions
  commands/*.md            Slash command definitions
  commands/*/*.md          Nested command definitions (e.g., openagents/)
  .codex-plugin/plugin.json  Plugin manifest

OVERLAY FILES (NOT checked — per-project):
  skills/**, config/**, scripts/**, hooks/**, assets/**,
  .claude-plugin/**, README.md, and any other file
USAGE
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --check)    MODE="check"; shift ;;
        --sync)     MODE="sync"; shift ;;
        --team)     TEAM="$2"; shift 2 ;;
        --team=*)   TEAM="${1#*=}"; shift ;;
        --project)  PROJECT="$2"; shift 2 ;;
        --project=*) PROJECT="${1#*=}"; shift ;;
        --plugins-dir) PLUGINS_DIR="$2"; shift 2 ;;
        --plugins-dir=*) PLUGINS_DIR="${1#*=}"; shift ;;
        -h|--help)  usage; exit 0 ;;
        *)          die "Unknown option: $1 (try --help)" ;;
    esac
done

# Validate mode
if [[ -z "$MODE" ]]; then
    usage
    exit 2
fi

if [[ "$MODE" != "check" && "$MODE" != "sync" ]]; then
    die "Invalid mode: $MODE (must be --check or --sync)"
fi

# Validate team
if [[ -z "$TEAM" ]]; then
    TEAM="all"
fi

case "$TEAM" in
    ram|durham|all) ;;
    *) die "Invalid team: $TEAM (must be ram, durham, or all)" ;;
esac

# Validate plugins directory
if [[ ! -d "$PLUGINS_DIR" ]]; then
    die "Plugins directory not found: $PLUGINS_DIR"
fi

# Determine which teams to process
declare -a teams_to_run
if [[ "$TEAM" == "all" ]]; then
    teams_to_run=("ram" "durham")
else
    teams_to_run=("$TEAM")
fi

log_info "Allura Harness Sync — mode: ${MODE}, team: ${TEAM}${PROJECT:+, project: ${PROJECT}}"
log_info "Plugins directory: ${PLUGINS_DIR}"

# --- Banner ---------------------------------------------------------------
printf "\n"
printf "${C_BOLD}╔══════════════════════════════════════════════════════════════╗${C_RESET}\n"
printf "${C_BOLD}║         Allura Harness Sync — Drift Detection & Repair       ║${C_RESET}\n"
printf "${C_BOLD}╚══════════════════════════════════════════════════════════════╝${C_RESET}\n"
printf "\n"
printf "${C_DIM}Core files:${C_RESET}    agents/*.md, commands/**/*.md, .codex-plugin/plugin.json\n"
printf "${C_DIM}Overlay files:${C_RESET} skills/**, config/**, scripts/**, hooks/**, assets/**, etc.\n"
printf "${C_DIM}Mode:${C_RESET}         %s\n" "$MODE"
printf "${C_DIM}Team:${C_RESET}         %s\n" "$TEAM"
printf "${C_DIM}Project:${C_RESET}      %s\n" "${PROJECT:-all}"
printf "\n"

# --- Main loop ------------------------------------------------------------

global_drift=0
global_synced=0

for team in "${teams_to_run[@]}"; do
    team_display=$(get_team_display "$team")
    canonical_dir=$(get_canonical "$team")

    if [[ ! -d "$canonical_dir" ]]; then
        log_warn "Canonical directory not found for ${team_display}: ${canonical_dir} — skipping"
        continue
    fi

    log_info "Processing team: ${team_display} (canonical: ${canonical_dir})"

    # Get project list
    if [[ -n "$PROJECT" ]]; then
        # Specific project — validate it exists
        project_dir="${PLUGINS_DIR}/${PROJECT}"
        if [[ ! -d "$project_dir" ]]; then
            log_warn "Project directory not found: ${project_dir} — skipping"
            continue
        fi

        if [[ "$MODE" == "check" ]]; then
            check_project "$canonical_dir" "$project_dir" "$PROJECT" "$team_display" || global_drift=1
        elif [[ "$MODE" == "sync" ]]; then
            sync_project "$canonical_dir" "$project_dir" "$PROJECT" "$team_display"
            ((global_synced++)) || true
        fi
    else
        # All projects for this team
        while IFS= read -r proj_name; do
            [[ -z "$proj_name" ]] && continue
            project_dir="${PLUGINS_DIR}/${proj_name}"

            if [[ ! -d "$project_dir" ]]; then
                log_warn "Project directory not found: ${project_dir} — skipping"
                continue
            fi

            if [[ "$MODE" == "check" ]]; then
                check_project "$canonical_dir" "$project_dir" "$proj_name" "$team_display" || global_drift=1
            elif [[ "$MODE" == "sync" ]]; then
                sync_project "$canonical_dir" "$project_dir" "$proj_name" "$team_display"
                ((global_synced++)) || true
            fi
        done < <(get_projects "$team")
    fi
done

# --- Final report ---------------------------------------------------------

printf "\n"
printf "${C_BOLD}═══════════════════════════════════════════════════════════════${C_RESET}\n"

if [[ "$MODE" == "check" ]]; then
    if [[ $global_drift -eq 0 ]]; then
        printf "${C_GREEN}${C_BOLD}  NO DRIFT — All core harness files are in sync.${C_RESET}\n"
        printf "\n"
        exit 0
    else
        printf "${C_RED}${C_BOLD}  CORE DRIFT FOUND — Some core harness files differ or are missing.${C_RESET}\n"
        printf "${C_RED}  Run with --sync to repair, or manually update the affected files.${C_RESET}\n"
        printf "\n"
        exit 1
    fi
elif [[ "$MODE" == "sync" ]]; then
    printf "${C_GREEN}${C_BOLD}  SYNC COMPLETE — ${global_synced} project(s) processed.${C_RESET}\n"
    printf "\n"
    exit 0
fi