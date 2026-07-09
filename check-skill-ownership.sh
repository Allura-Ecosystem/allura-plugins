#!/usr/bin/env bash
#
# check-skill-ownership.sh
#
# Scans ~/.hermes/skills/ for SKILL.md files, checks ownership from
# YAML frontmatter (owner: field) and a canonical manifest
# (SKILL-OWNERSHIP.json). Reports orphan skills and exits non-zero
# if any are found, making it CI-enforceable.
#
# Usage:
#   check-skill-ownership.sh [--json-only]
#
#   --json-only   Only use SKILL-OWNERSHIP.json; ignore frontmatter owners.
#
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${HOME}/.hermes/skills"
OWNERSHIP_FILE="${SKILLS_DIR}/SKILL-OWNERSHIP.json"
JSON_ONLY=false

[[ "${1:-}" == "--json-only" ]] && JSON_ONLY=true

#
# --- Helpers -----------------------------------------------------------------
#

# Extract a YAML frontmatter field from a SKILL.md file.
# Usage: extract_field <file> <field_name>
# Returns the value or empty string if not found.
extract_field() {
    local file="$1"
    local field="$2"
    # Read frontmatter (between --- markers) and grab the field
    awk -v fld="^${field}:" '
        /^---$/ { in_fm = !in_fm; next }
        in_fm && $0 ~ fld {
            # Strip the field name and leading whitespace
            sub("^" fld "[[:space:]]*", "")
            gsub(/^[[:space:]]+|[[:space:]]+$/, "")
            gsub(/^["'"'"']|["'"'"']$/, "")
            print
            exit
        }
    ' "$file"
}

# Simple JSON value extraction (no jq dependency, but use jq if available).
# Usage: json_get <file> <key>
json_get() {
    local file="$1"
    local key="$2"
    if command -v jq &>/dev/null; then
        jq -r --arg k "$key" '.skills[$k] // empty' "$file" 2>/dev/null
    else
        # Fallback: grep for "key": "value" pattern
        grep -oP "\"${key}\"\s*:\s*\"?\K[^\"\n,}]+" "$file" 2>/dev/null | head -1 | sed 's/[[:space:]]*$//'
    fi
}

# Create the template ownership manifest with all discovered skills as orphans.
create_template_manifest() {
    local manifest="$1"
    shift
    local skills_json=""
    local first=true

    # Build the skills object from arguments (skill-name pairs)
    for skill_name in "$@"; do
        if $first; then
            first=false
        else
            skills_json+=","
        fi
        skills_json+="    \"${skill_name}\": \"\""
    done

    cat > "$manifest" <<EOF
{
  "version": 1,
  "skills": {
${skills_json}
  }
}
EOF
}

#
# --- Main --------------------------------------------------------------------
#

if [[ ! -d "$SKILLS_DIR" ]]; then
    echo "ERROR: Skills directory not found: $SKILLS_DIR" >&2
    exit 2
fi

# Collect all SKILL.md files
mapfile -t SKILL_FILES < <(find "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null | sort)

TOTAL=${#SKILL_FILES[@]}

if [[ "$TOTAL" -eq 0 ]]; then
    echo "SKILL OWNERSHIP REPORT"
    echo "======================"
    echo "Total skills: 0"
    echo "Owned: 0"
    echo "Orphans: 0"
    echo "Duplicate owners: 0"
    echo ""
    echo "No SKILL.md files found in $SKILLS_DIR"
    echo ""
    echo "PASS"
    exit 0
fi

# Ensure ownership manifest exists; create template if missing
MANIFEST_CREATED=false
if [[ ! -f "$OWNERSHIP_FILE" ]]; then
    # Collect skill names for the template
    skill_names=()
    for f in "${SKILL_FILES[@]}"; do
        name=$(extract_field "$f" "name")
        [[ -z "$name" ]] && name=$(basename "$(dirname "$f")")
        skill_names+=("$name")
    done
    create_template_manifest "$OWNERSHIP_FILE" "${skill_names[@]}"
    MANIFEST_CREATED=true
    echo "INFO: Created template ownership manifest at $OWNERSHIP_FILE" >&2
    echo "INFO: All skills listed as orphans (empty owner). Fill in owners and re-run." >&2
fi

# --- Classify each skill ------------------------------------------------------
declare -A SKILL_PATHS        # skill_name -> path
declare -A SKILL_OWNERS       # skill_name -> owner (from frontmatter or manifest)
declare -A OWNER_COUNT        # owner -> count of skills owned
ORPHAN_NAMES=()
ORPHAN_PATHS=()

for f in "${SKILL_FILES[@]}"; do
    # Extract skill name from frontmatter, fallback to directory name
    skill_name=$(extract_field "$f" "name")
    if [[ -z "$skill_name" ]]; then
        skill_name=$(basename "$(dirname "$f")")
    fi

    SKILL_PATHS["$skill_name"]="$f"

    # Determine owner: check frontmatter first (unless --json-only), then manifest
    owner=""

    if [[ "$JSON_ONLY" == false ]]; then
        owner=$(extract_field "$f" "owner")
    fi

    if [[ -z "$owner" ]]; then
        # Check the canonical manifest
        owner=$(json_get "$OWNERSHIP_FILE" "$skill_name")
    fi

    if [[ -n "$owner" ]]; then
        SKILL_OWNERS["$skill_name"]="$owner"
        OWNER_COUNT["$owner"]=$(( ${OWNER_COUNT["$owner"]:-0} + 1 ))
    else
        ORPHAN_NAMES+=("$skill_name")
        ORPHAN_PATHS+=("$f")
    fi
done

OWNED=${#SKILL_OWNERS[@]}
ORPHAN_COUNT=${#ORPHAN_NAMES[@]}

# Count duplicate owners (owners with more than 1 skill)
DUPLICATE_OWNERS=0
DUPLICATE_OWNER_NAMES=()
for owner in "${!OWNER_COUNT[@]}"; do
    if [[ "${OWNER_COUNT[$owner]}" -gt 1 ]]; then
        DUPLICATE_OWNERS=$((DUPLICATE_OWNERS + 1))
        DUPLICATE_OWNER_NAMES+=("$owner (${OWNER_COUNT[$owner]} skills)")
    fi
done

# --- Report -------------------------------------------------------------------
echo ""
echo "SKILL OWNERSHIP REPORT"
echo "======================"
echo "Total skills:       $TOTAL"
echo "Owned:              $OWNED"
echo "Orphans:            $ORPHAN_COUNT"
echo "Duplicate owners:   $DUPLICATE_OWNERS"
echo ""

if [[ "$ORPHAN_COUNT" -gt 0 ]]; then
    echo "ORPHAN SKILLS:"
    for i in "${!ORPHAN_NAMES[@]}"; do
        echo "  - ${ORPHAN_NAMES[$i]} (${ORPHAN_PATHS[$i]})"
    done
    echo ""
fi

if [[ "$DUPLICATE_OWNERS" -gt 0 ]]; then
    echo "DUPLICATE OWNERS:"
    for entry in "${DUPLICATE_OWNER_NAMES[@]}"; do
        echo "  - $entry"
    done
    echo ""
fi

if [[ "$MANIFEST_CREATED" == true ]]; then
    echo "NOTE: A template SKILL-OWNERSHIP.json was created. Edit it to assign owners."
    echo ""
fi

# --- Exit code ----------------------------------------------------------------
if [[ "$ORPHAN_COUNT" -gt 0 ]]; then
    echo "FAIL"
    exit 1
else
    echo "PASS"
    exit 0
fi