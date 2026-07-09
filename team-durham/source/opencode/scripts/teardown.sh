#!/bin/bash
# Brand Maker — Session Teardown Script
# Logs session summary, archives state, and cleans temp files
# Usage: bash .opencode/scripts/teardown.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  Brand Maker — Session Teardown"
echo "========================================"
echo ""

# ── Archive State ────────────────────────────────────────
STATE_DIR=".opencode/state"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
STATE_FILE="${STATE_DIR}/session-${TIMESTAMP}.json"

mkdir -p "$STATE_DIR"

echo -e "${BLUE}💾 Archiving Session State${NC}"

# Count client deliverables
DELIVERABLE_COUNT=0
if [ -d "clients" ]; then
    DELIVERABLE_COUNT=$(find clients -name "0*.md" -o -name "0*.json" 2>/dev/null | wc -l)
fi

# Count events (if DB available)
EVENT_COUNT="N/A"
if command -v docker &> /dev/null; then
    EVENT_COUNT=$(docker exec knowledge-postgres psql -U ronin4life -d memory -t -c "SELECT COUNT(*) FROM events WHERE group_id = 'allura-team-durham';" 2>/dev/null | tr -d ' ' || echo "N/A")
fi

# Write state snapshot
cat > "$STATE_FILE" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "deliverables": $DELIVERABLE_COUNT,
  "events_count": "$EVENT_COUNT",
  "agents_active": 9,
  "group_id": "allura-team-durham",
  "current_client": "ember-fold"
}
EOF

echo -e "   ${GREEN}✅${NC} State saved: $STATE_FILE"
echo ""

# ── Clean Temp Files ─────────────────────────────────────
echo -e "${BLUE}🧹 Cleaning Temp Files${NC}"

TEMP_PATTERNS=(".tmp/tasks" "*.log" "execution-log.txt")

for pattern in "${TEMP_PATTERNS[@]}"; do
    if [ -d "$pattern" ]; then
        COUNT=$(find "$pattern" -type f 2>/dev/null | wc -l)
        if [ $COUNT -gt 0 ]; then
            # Don't auto-delete task files — just report
            echo -e "   ${YELLOW}⚠️${NC}  $pattern ($COUNT files — preserved)"
        fi
    fi
done
echo ""

# ── Summary ───────────────────────────────────────────────
echo "========================================"
echo -e "  ${GREEN}✅ Teardown complete${NC}"
echo "  State: $STATE_FILE"
echo "  Next: Run .opencode/scripts/bootstrap.sh to validate"
echo "========================================"