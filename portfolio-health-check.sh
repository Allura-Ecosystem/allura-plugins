#!/usr/bin/env bash
###############################################################################
# portfolio-health-check.sh — Tier 3 Cross-Project Health Check
#
# Scans ALL projects across the portfolio for problems that no single-project
# gate can catch. Implements the deferred Tier 3 from the Three-Tier Governance
# Model (Brain memory e8ba3a55).
#
# Checks:
#   1. HARNESS DRIFT         — runs harness-sync.sh --check --team all
#   2. SECRETS IN COMMITS    — scans recent commits for secret-like patterns
#   3. GOVERNANCE DOC SYNC   — verifies canonical six docs per project
#   4. TEST INFRASTRUCTURE   — checks for test runners (package.json/Makefile)
#   5. SKILL ORPHANS         — runs check-skill-ownership.sh
#
# Usage:
#   portfolio-health-check.sh                           # scan default dirs
#   portfolio-health-check.sh --projects-dir /path      # add a projects dir
#   portfolio-health-check.sh --json                   # machine-readable output
#
# Exit codes:
#   0 — HEALTHY (all checks pass)
#   1 — NEEDS ATTENTION (some checks fail, not critical)
#   2 — CRITICAL (secrets found or multiple critical failures)
###############################################################################

set -uo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_SYNC="${SCRIPT_DIR}/harness-sync.sh"
SKILL_OWNERSHIP="${SCRIPT_DIR}/check-skill-ownership.sh"

# Default project directories to scan
DEFAULT_PROJECT_DIRS=("$HOME/plugins" "/media/ronin704/Games/Repos")

# Canonical governance docs
GOVERNANCE_DOCS=(
    "BLUEPRINT.md"
    "SOLUTION-ARCHITECTURE.md"
    "DESIGN-ALLURA.md"
    "REQUIREMENTS-MATRIX.md"
    "RISKS-AND-DECISIONS.md"
    "DATA-DICTIONARY.md"
)

# Secret patterns (grep extended regex)
SECRET_PATTERS=(
    'sk-[A-Za-z0-9]{20,}'
    'ntn_[A-Za-z0-9]{20,}'
    'secret_[A-Za-z0-9]{16,}'
    'Bearer\s+[A-Za-z0-9_\.\-]{20,}'
    'token=[A-Za-z0-9_\.\-]{16,}'
    'BEGIN RSA PRIVATE KEY'
    'BEGIN PGP PRIVATE KEY'
    'postgres://[A-Za-z0-9_]+:[^@]+@'
    'mongodb(\+srv)?://[A-Za-z0-9_]+:[^@]+@'
)
SECRET_REGEX=$(IFS='|'; echo "${SECRET_PATTERS[*]}")

# Flags
JSON_OUTPUT=false
EXTRA_PROJECT_DIRS=()
COMMIT_SCAN_COUNT=100

# Colors
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

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log_info()  { printf "${C_CYAN}[INFO]${C_RESET}  %s\n" "$*" >&2; }
log_warn()  { printf "${C_YELLOW}[WARN]${C_RESET}  %s\n" "$*" >&2; }
log_error() { printf "${C_RED}[ERROR]${C_RESET} %s\n" "$*" >&2; }

die() { log_error "$@"; exit 2; }

# Build the full list of project directories to scan
get_all_project_dirs() {
    local all_dirs=()
    for d in "${DEFAULT_PROJECT_DIRS[@]}" "${EXTRA_PROJECT_DIRS[@]}"; do
        if [[ -d "$d" ]]; then
            all_dirs+=("$d")
        fi
    done
    printf '%s\n' "${all_dirs[@]}"
}

# Find all git repos within the project directories (including submodules)
# Returns absolute paths to repos (dirs containing .git)
find_git_repos() {
    local search_dir
    while IFS= read -r search_dir; do
        [[ -z "$search_dir" ]] && continue
        # Find .git dirs (repos) — but avoid nested .git inside already found repos
        find "$search_dir" -name ".git" -type d 2>/dev/null | while read -r gitdir; do
            dirname "$gitdir"
        done
        # Also find .git files (submodules) — these are gitdir pointers
        find "$search_dir" -name ".git" -type f 2>/dev/null | while read -r gitfile; do
            dirname "$gitfile"
        done
    done < <(get_all_project_dirs)
}

# Find all "project" directories — top-level subdirs in each projects-dir,
# plus the projects-dir itself if it has governance docs or is a repo
discover_projects() {
    local search_dir
    while IFS= read -r search_dir; do
        [[ -z "$search_dir" ]] && continue
        # The search dir itself could be a project
        if [[ -d "${search_dir}/docs/allura" ]] || [[ -f "${search_dir}/package.json" ]] || [[ -f "${search_dir}/Makefile" ]]; then
            echo "$search_dir"
        fi
        # Each immediate subdirectory is a project candidate
        for subdir in "$search_dir"/*/; do
            [[ -d "$subdir" ]] || continue
            # Skip hidden dirs and common non-project dirs
            local base
            base=$(basename "$subdir")
            [[ "$base" == .* ]] && continue
            [[ "$base" == "node_modules" ]] && continue
            echo "${subdir%/}"
        done
    done < <(get_all_project_dirs)
}

# ---------------------------------------------------------------------------
# Check 1: Harness Drift
# ---------------------------------------------------------------------------
check_harness_drift() {
    local output exit_code
    if [[ ! -x "$HARNESS_SYNC" ]] && [[ ! -f "$HARNESS_SYNC" ]]; then
        HARNESS_DRIFT_STATUS="FAIL"
        HARNESS_DRIFT_DETAIL="harness-sync.sh not found at $HARNESS_SYNC"
        HARNESS_DRIFT_OUTPUT=""
        return
    fi

    output=$(bash "$HARNESS_SYNC" --check --team all 2>&1) || true
    exit_code=$?

    HARNESS_DRIFT_OUTPUT="$output"
    if [[ $exit_code -eq 0 ]]; then
        HARNESS_DRIFT_STATUS="PASS"
        HARNESS_DRIFT_DETAIL="No drift detected across all teams"
    elif [[ $exit_code -eq 1 ]]; then
        HARNESS_DRIFT_STATUS="FAIL"
        # Extract drift summary from output
        local drift_lines
        drift_lines=$(echo "$output" | grep -i 'drift\|missing\|CORE DRIFT' | head -5)
        HARNESS_DRIFT_DETAIL="Drift detected: ${drift_lines}"
    else
        HARNESS_DRIFT_STATUS="FAIL"
        HARNESS_DRIFT_DETAIL="harness-sync.sh exited with code $exit_code"
    fi
}

# ---------------------------------------------------------------------------
# Check 2: Secrets in Commits
# ---------------------------------------------------------------------------
check_secrets_in_commits() {
    local repos
    mapfile -t repos < <(find_git_repos | sort -u)

    SECRETS_FOUND=0
    SECRETS_DETAILS=""

    for repo in "${repos[@]}"; do
        [[ -z "$repo" ]] && continue
        [[ -d "$repo/.git" || -f "$repo/.git" ]] || continue

        local repo_name
        repo_name=$(basename "$repo")

        # Efficient approach: pipe git log -p directly to a processing script
        # Use awk to track commit hash and file, grep for secrets on added lines only
        local results
        results=$(git -C "$repo" log "-${COMMIT_SCAN_COUNT}" -p \
            --format='__COMMIT__%H' \
            --no-color 2>/dev/null | \
            awk '
                /^__COMMIT__/ { commit = substr($0, 11); file = ""; next }
                /^diff --git a\// {
                    match($0, /diff --git a\/([^ ]+)/, m)
                    file = m[1]
                    next
                }
                /^\+\+\+/ { next }
                /^\+/ {
                    line = substr($0, 2)
                    if (line ~ /sk-[A-Za-z0-9]{20,}/ ||
                        line ~ /ntn_[A-Za-z0-9]{20,}/ ||
                        line ~ /secret_[A-Za-z0-9]{16,}/ ||
                        line ~ /Bearer[ \t]+[A-Za-z0-9_.-]{20,}/ ||
                        line ~ /token=[A-Za-z0-9_.-]{16,}/ ||
                        line ~ /BEGIN RSA PRIVATE KEY/ ||
                        line ~ /BEGIN PGP PRIVATE KEY/ ||
                        line ~ /postgres:\/\/[A-Za-z0-9_]+:[^@]+@/ ||
                        line ~ /mongodb(\+srv)?:\/\/[A-Za-z0-9_]+:[^@]+@/) {
                        printf "%s %s %s\n", substr(commit, 1, 8), file, substr(line, 1, 120)
                    }
                }
            ' 2>/dev/null) || continue

        if [[ -n "$results" ]]; then
            while IFS= read -r result_line; do
                [[ -z "$result_line" ]] && continue
                ((SECRETS_FOUND++))
                # result_line format: "short_hash file snippet"
                local short_hash file snippet
                short_hash=$(echo "$result_line" | awk '{print $1}')
                file=$(echo "$result_line" | awk '{print $2}')
                snippet=$(echo "$result_line" | cut -d' ' -f3-)
                SECRETS_DETAILS+="  ${repo_name} ${short_hash} ${file}: ${snippet}\n"
            done <<< "$results"
        fi
    done

    if [[ $SECRETS_FOUND -eq 0 ]]; then
        SECRETS_STATUS="PASS"
        SECRETS_DETAIL="0 secrets found across ${#repos[@]} repos"
    else
        SECRETS_STATUS="FAIL"
        SECRETS_DETAIL="${SECRETS_FOUND} potential secrets found"
    fi
}

# ---------------------------------------------------------------------------
# Check 3: Governance Doc Sync
# ---------------------------------------------------------------------------
check_governance_docs() {
    local projects
    mapfile -t projects < <(discover_projects | sort -u)

    GOV_MISSING_COUNT=0
    GOV_MISSING_DETAILS=""
    GOV_PROJECTS_WITH_DOCS=0

    for proj in "${projects[@]}"; do
        [[ -z "$proj" ]] && continue
        local docs_dir="${proj}/docs/allura"

        if [[ ! -d "$docs_dir" ]]; then
            # No docs/allura at all — only report if it looks like a real project
            # (has some source files or package.json)
            if [[ -f "${proj}/package.json" ]] || [[ -f "${proj}/Makefile" ]] || [[ -f "${proj}/AGENTS.md" ]]; then
                local proj_name
                proj_name=$(basename "$proj")
                for doc in "${GOVERNANCE_DOCS[@]}"; do
                    ((GOV_MISSING_COUNT++))
                    GOV_MISSING_DETAILS+="  ${proj_name}: missing ${doc} (no docs/allura/ dir)\n"
                done
            fi
            continue
        fi

        ((GOV_PROJECTS_WITH_DOCS++))
        local proj_name
        proj_name=$(basename "$proj")
        for doc in "${GOVERNANCE_DOCS[@]}"; do
            if [[ ! -f "${docs_dir}/${doc}" ]]; then
                ((GOV_MISSING_COUNT++))
                GOV_MISSING_DETAILS+="  ${proj_name}: missing ${doc}\n"
            fi
        done
    done

    if [[ $GOV_MISSING_COUNT -eq 0 ]]; then
        GOV_STATUS="PASS"
        GOV_DETAIL="All canonical docs present in ${GOV_PROJECTS_WITH_DOCS} projects with docs/allura/"
    else
        GOV_STATUS="FAIL"
        GOV_DETAIL="${GOV_MISSING_COUNT} missing docs across portfolio"
    fi
}

# ---------------------------------------------------------------------------
# Check 4: Test Infrastructure (DoD Loop Gaps)
# ---------------------------------------------------------------------------
check_test_infrastructure() {
    local projects
    mapfile -t projects < <(discover_projects | sort -u)

    TEST_NO_INFRA=0
    TEST_NO_INFRA_PROJECTS=""
    TEST_HAS_INFRA=0

    for proj in "${projects[@]}"; do
        [[ -z "$proj" ]] && continue
        local proj_name
        proj_name=$(basename "$proj")
        local has_tests=false

        # Check for package.json with a "test" script
        if [[ -f "${proj}/package.json" ]]; then
            if grep -q '"test"' "${proj}/package.json" 2>/dev/null; then
                has_tests=true
            fi
        fi

        # Check for Makefile with a test target
        if [[ "$has_tests" == false ]] && [[ -f "${proj}/Makefile" ]]; then
            if grep -qE '^test:' "${proj}/Makefile" 2>/dev/null; then
                has_tests=true
            fi
        fi

        # Check for common test directories/files (pytest, jest, etc.)
        if [[ "$has_tests" == false ]]; then
            if find "$proj" -maxdepth 3 -name "test_*.py" -o -name "*_test.py" -o -name "*.test.ts" -o -name "*.test.js" -o -name "*.spec.ts" -o -name "*.spec.js" 2>/dev/null | head -1 | grep -q .; then
                has_tests=true
            fi
        fi

        if [[ "$has_tests" == true ]]; then
            ((TEST_HAS_INFRA++))
        else
            # Only report if it looks like a real code project
            if [[ -f "${proj}/package.json" ]] || [[ -f "${proj}/Makefile" ]] || [[ -f "${proj}/AGENTS.md" ]] || [[ -f "${proj}/pyproject.toml" ]]; then
                ((TEST_NO_INFRA++))
                TEST_NO_INFRA_PROJECTS+="${proj_name} "
            fi
        fi
    done

    if [[ $TEST_NO_INFRA -eq 0 ]]; then
        TEST_STATUS="PASS"
        TEST_DETAIL="All ${TEST_HAS_INFRA} code projects have test infrastructure"
    else
        TEST_STATUS="FAIL"
        TEST_DETAIL="${TEST_NO_INFRA} projects without test infrastructure: ${TEST_NO_INFRA_PROJECTS% }"
    fi
}

# ---------------------------------------------------------------------------
# Check 5: Skill Orphans
# ---------------------------------------------------------------------------
check_skill_orphans() {
    local output exit_code
    if [[ ! -f "$SKILL_OWNERSHIP" ]]; then
        SKILL_ORPHAN_STATUS="FAIL"
        SKILL_ORPHAN_DETAIL="check-skill-ownership.sh not found at $SKILL_OWNERSHIP"
        SKILL_ORPHAN_COUNT=0
        return
    fi

    output=$(bash "$SKILL_OWNERSHIP" 2>&1) || true
    exit_code=$?

    SKILL_ORPHAN_OUTPUT="$output"
    # Extract orphan count from "Orphans: N" line
    SKILL_ORPHAN_COUNT=$(echo "$output" | grep -oP 'Orphans:\s+\K[0-9]+' 2>/dev/null || echo "0")

    if [[ $SKILL_ORPHAN_COUNT -eq 0 ]]; then
        SKILL_ORPHAN_STATUS="PASS"
        SKILL_ORPHAN_DETAIL="0 orphan skills"
    else
        SKILL_ORPHAN_STATUS="FAIL"
        SKILL_ORPHAN_DETAIL="${SKILL_ORPHAN_COUNT} orphan skills found"
    fi
}

# ---------------------------------------------------------------------------
# JSON Output
# ---------------------------------------------------------------------------
emit_json() {
    local date_str
    date_str=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local project_count
    project_count=$(discover_projects | sort -u | wc -l)

    # Determine overall status
    local overall="HEALTHY"
    local exit_code=0
    local fail_count=0
    local critical=false

    [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SECRETS_STATUS" == "FAIL" ]] && { critical=true; ((fail_count++)); }
    [[ "$GOV_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$TEST_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SKILL_ORPHAN_STATUS" == "FAIL" ]] && ((fail_count++))

    if $critical; then
        overall="CRITICAL"
        exit_code=2
    elif [[ $fail_count -gt 0 ]]; then
        overall="NEEDS ATTENTION"
        exit_code=1
    fi

    # Build recommendations array
    local recs=()
    [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]] && recs+=("\"Run harness-sync.sh --sync to fix drift\"")
    [[ "$SECRETS_STATUS" == "FAIL" ]] && recs+=("\"CRITICAL: Review and rotate exposed secrets immediately\"")
    [[ "$GOV_STATUS" == "FAIL" ]] && recs+=("\"Create missing governance docs in projects lacking docs/allura/\"")
    [[ "$TEST_STATUS" == "FAIL" ]] && recs+=("\"Add test infrastructure (package.json test script or Makefile test target) to: ${TEST_NO_INFRA_PROJECTS% }\"")
    [[ "$SKILL_ORPHAN_STATUS" == "FAIL" ]] && recs+=("\"Assign owners to ${SKILL_ORPHAN_COUNT} orphan skills in SKILL-OWNERSHIP.json\"")
    [[ ${#recs[@]} -eq 0 ]] && recs+=("\"Portfolio is healthy — no action needed\"")

    local recs_json
    recs_json=$(IFS=','; echo "${recs[*]}")

    cat <<EOF
{
  "report": "portfolio-health-check",
  "date": "${date_str}",
  "projects_scanned": ${project_count},
  "checks": {
    "harness_drift": {
      "status": "${HARNESS_DRIFT_STATUS}",
      "detail": $(echo "$HARNESS_DRIFT_DETAIL" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))' 2>/dev/null || echo '"error"')
    },
    "secrets_in_commits": {
      "status": "${SECRETS_STATUS}",
      "count": ${SECRETS_FOUND},
      "detail": "${SECRETS_DETAIL}"
    },
    "governance_docs": {
      "status": "${GOV_STATUS}",
      "missing_count": ${GOV_MISSING_COUNT},
      "detail": "${GOV_DETAIL}"
    },
    "test_infrastructure": {
      "status": "${TEST_STATUS}",
      "projects_without_tests": ${TEST_NO_INFRA},
      "detail": $(echo "$TEST_DETAIL" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))' 2>/dev/null || echo '"error"')
    },
    "skill_orphans": {
      "status": "${SKILL_ORPHAN_STATUS}",
      "count": ${SKILL_ORPHAN_COUNT},
      "detail": "${SKILL_ORPHAN_DETAIL}"
    }
  },
  "overall": "${overall}",
  "exit_code": ${exit_code},
  "recommendations": [${recs_json}]
}
EOF
}

# ---------------------------------------------------------------------------
# Text Report Output
# ---------------------------------------------------------------------------
emit_text_report() {
    local date_str
    date_str=$(date -u '+%Y-%m-%d %H:%M UTC')
    local project_count
    project_count=$(discover_projects | sort -u | wc -l)

    # Determine overall status
    local overall="HEALTHY"
    local exit_code=0
    local fail_count=0
    local critical=false

    [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SECRETS_STATUS" == "FAIL" ]] && { critical=true; ((fail_count++)); }
    [[ "$GOV_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$TEST_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SKILL_ORPHAN_STATUS" == "FAIL" ]] && ((fail_count++))

    if $critical; then
        overall="CRITICAL"
        exit_code=2
    elif [[ $fail_count -gt 0 ]]; then
        overall="NEEDS ATTENTION"
        exit_code=1
    fi

    printf "\n"
    printf "${C_BOLD}PORTFOLIO HEALTH CHECK REPORT${C_RESET}\n"
    printf "============================\n"
    printf "Date: %s\n" "$date_str"
    printf "Projects scanned: %d\n" "$project_count"
    printf "\n"

    # 1. Harness Drift
    local s_color
    [[ "$HARNESS_DRIFT_STATUS" == "PASS" ]] && s_color="$C_GREEN" || s_color="$C_RED"
    printf "1. HARNESS DRIFT: ${s_color}[%s]${C_RESET} %s\n" "$HARNESS_DRIFT_STATUS" "$HARNESS_DRIFT_DETAIL"
    if [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]]; then
        echo "$HARNESS_DRIFT_OUTPUT" | grep -E 'DRIFT|MISSING|Summary|Project:' | head -10 | sed 's/^/   /'
    fi

    # 2. Secrets
    [[ "$SECRETS_STATUS" == "PASS" ]] && s_color="$C_GREEN" || s_color="$C_RED"
    printf "2. SECRETS IN COMMITS: ${s_color}[%s]${C_RESET} %s found\n" "$SECRETS_STATUS" "$SECRETS_FOUND"
    if [[ $SECRETS_FOUND -gt 0 ]]; then
        printf "$C_RED"
        printf "$SECRETS_DETAILS"
        printf "$C_RESET"
    fi

    # 3. Governance Docs
    [[ "$GOV_STATUS" == "PASS" ]] && s_color="$C_GREEN" || s_color="$C_YELLOW"
    printf "3. GOVERNANCE DOCS: ${s_color}[%s]${C_RESET} %s\n" "$GOV_STATUS" "$GOV_DETAIL"
    if [[ $GOV_MISSING_COUNT -gt 0 ]]; then
        printf "$C_DIM"
        printf "$GOV_MISSING_DETAILS"
        printf "$C_RESET"
    fi

    # 4. Test Infrastructure
    [[ "$TEST_STATUS" == "PASS" ]] && s_color="$C_GREEN" || s_color="$C_YELLOW"
    printf "4. TEST INFRASTRUCTURE: ${s_color}[%s]${C_RESET} %s\n" "$TEST_STATUS" "$TEST_DETAIL"

    # 5. Skill Orphans
    [[ "$SKILL_ORPHAN_STATUS" == "PASS" ]] && s_color="$C_GREEN" || s_color="$C_YELLOW"
    printf "5. SKILL ORPHANS: ${s_color}[%s]${C_RESET} %s\n" "$SKILL_ORPHAN_STATUS" "$SKILL_ORPHAN_DETAIL"

    # Overall
    printf "\n"
    local overall_color
    case "$overall" in
        HEALTHY)           overall_color="$C_GREEN" ;;
        "NEEDS ATTENTION") overall_color="$C_YELLOW" ;;
        CRITICAL)          overall_color="$C_RED" ;;
    esac
    printf "${C_BOLD}OVERALL: ${overall_color}%s${C_RESET}\n" "$overall"

    # Recommendations
    printf "\n"
    printf "${C_BOLD}RECOMMENDATIONS:${C_RESET}\n"
    if [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]]; then
        printf "  - Run ~/plugins/harness-sync.sh --sync to fix harness drift\n"
    fi
    if [[ "$SECRETS_STATUS" == "FAIL" ]]; then
        printf "  - ${C_RED}${C_BOLD}CRITICAL: Review and rotate exposed secrets immediately${C_RESET}\n"
        printf "  - Audit git history with: git log -p -S'PATTERN' in affected repos\n"
    fi
    if [[ "$GOV_STATUS" == "FAIL" ]]; then
        printf "  - Create missing governance docs in projects lacking docs/allura/\n"
        printf "  - Use canonical templates from allura-memory/docs/allura/ as reference\n"
    fi
    if [[ "$TEST_STATUS" == "FAIL" ]]; then
        printf "  - Add test infrastructure to: %s\n" "${TEST_NO_INFRA_PROJECTS% }"
        printf "  - Minimum: package.json with 'test' script or Makefile with 'test:' target\n"
    fi
    if [[ "$SKILL_ORPHAN_STATUS" == "FAIL" ]]; then
        printf "  - Assign owners to %d orphan skills in ~/.hermes/skills/SKILL-OWNERSHIP.json\n" "$SKILL_ORPHAN_COUNT"
    fi
    if [[ $fail_count -eq 0 ]]; then
        printf "  - Portfolio is healthy — no action needed\n"
    fi
    printf "\n"

    return $exit_code
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------

usage() {
    cat <<'USAGE'
portfolio-health-check.sh — Tier 3 Cross-Project Health Check

USAGE:
  portfolio-health-check.sh [OPTIONS]

OPTIONS:
  --projects-dir DIR   Add a projects directory to scan (can be repeated)
                       Default: ~/plugins and /media/ronin704/Games/Repos
  --json               Output machine-readable JSON instead of text report
  --commit-scan N      Number of recent commits to scan for secrets (default: 100)
  -h, --help           Show this help message

CHECKS:
  1. Harness Drift       — runs harness-sync.sh --check --team all
  2. Secrets in Commits  — scans git history for secret-like patterns
  3. Governance Docs     — verifies canonical six docs per project
  4. Test Infrastructure — checks for test runners in each project
  5. Skill Orphans       — runs check-skill-ownership.sh

EXIT CODES:
  0 — HEALTHY (all checks pass)
  1 — NEEDS ATTENTION (some checks fail, not critical)
  2 — CRITICAL (secrets found or severe issues)
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --projects-dir)
            EXTRA_PROJECT_DIRS+=("$2")
            shift 2
            ;;
        --projects-dir=*)
            EXTRA_PROJECT_DIRS+=("${1#*=}")
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        --commit-scan)
            COMMIT_SCAN_COUNT="$2"
            shift 2
            ;;
        --commit-scan=*)
            COMMIT_SCAN_COUNT="${1#*=}"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            die "Unknown option: $1 (try --help)"
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

log_info "Starting Portfolio Health Check..."

# Run all checks (collect data first, report at end)
log_info "Check 1/5: Harness Drift"
check_harness_drift

log_info "Check 2/5: Secrets in Commits"
check_secrets_in_commits

log_info "Check 3/5: Governance Doc Sync"
check_governance_docs

log_info "Check 4/5: Test Infrastructure"
check_test_infrastructure

log_info "Check 5/5: Skill Orphans"
check_skill_orphans

log_info "All checks complete. Generating report..."

# Emit report
if $JSON_OUTPUT; then
    emit_json
    # Determine exit code from overall
    fail_count=0
    critical=false
    [[ "$HARNESS_DRIFT_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SECRETS_STATUS" == "FAIL" ]] && { critical=true; ((fail_count++)); }
    [[ "$GOV_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$TEST_STATUS" == "FAIL" ]] && ((fail_count++))
    [[ "$SKILL_ORPHAN_STATUS" == "FAIL" ]] && ((fail_count++))
    if $critical; then
        exit 2
    elif [[ $fail_count -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
else
    emit_text_report
    exit $?
fi