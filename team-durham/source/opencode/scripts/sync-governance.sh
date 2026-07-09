#!/bin/bash
# Brand Maker — Governance Sync Script
# Pulls Team Durham roster and rules from Notion Agent OS
# Updates local .opencode/ files with latest governance data
# Usage: bash .opencode/scripts/sync-governance.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  Brand Maker — Governance Sync"
echo "========================================"
echo ""

SYNC_DIR=".opencode"

# ── Agent Metadata ───────────────────────────────────────
echo -e "${BLUE}📋 Agent Metadata${NC}"
echo "   Current: $(cat ${SYNC_DIR}/config/agent-metadata.json | grep -c '"id"' 2>/dev/null || echo '0') agents registered"
echo "   Note: Full Notion sync requires MCP_DOCKER tools (run with agents connected)"
echo ""

# ── Rules Sync ────────────────────────────────────────────
echo -e "${BLUE}📜 Rules${NC}"
RULES=(
    "agent-routing.md"
    "mcp-integration.md"
    "neo4j-best-practices.md"
    "postgres-best-practices.md"
)

for rule in "${RULES[@]}"; do
    if [ -f "${SYNC_DIR}/rules/${rule}" ]; then
        LINES=$(wc -l < "${SYNC_DIR}/rules/${rule}")
        echo -e "   ${GREEN}✅${NC} ${rule} (${LINES} lines)"
    else
        echo -e "   ${RED}❌${NC} ${rule} (MISSING)"
    fi
done
echo ""

# ── Templates Sync ────────────────────────────────────────
echo -e "${BLUE}📄 Templates${NC}"
TEMPLATES=(
    "BLUEPRINT.template.md"
    "DDR.template.md"
    "BRAND-DICTIONARY.template.md"
)

for template in "${TEMPLATES[@]}"; do
    if [ -f "${SYNC_DIR}/templates/${template}" ]; then
        echo -e "   ${GREEN}✅${NC} ${template}"
    else
        echo -e "   ${RED}❌${NC} ${template} (MISSING)"
    fi
done
echo ""

# ── Context Sync ──────────────────────────────────────────
echo -e "${BLUE}🗂️  Context Files${NC}"
CONTEXT_DIRS=("allura" "core" "project")
for dir in "${CONTEXT_DIRS[@]}"; do
    COUNT=$(find "${SYNC_DIR}/context/${dir}" -type f 2>/dev/null | wc -l)
    if [ $COUNT -gt 0 ]; then
        echo -e "   ${GREEN}✅${NC} ${dir}/ (${COUNT} files)"
    else
        echo -e "   ${YELLOW}⚠️${NC}  ${dir}/ (empty)"
    fi
done
echo ""

# ── Manual Notion Sync Instructions ───────────────────────
echo "========================================"
echo -e "${BLUE}📋 Manual Notion Sync${NC}"
echo ""
echo "To sync from Notion Agent OS:"
echo "  1. Connect MCP_DOCKER tools (docker compose up)"
echo "  2. Run: /sync-governance command"
echo "  3. Or manually fetch:"
echo "     - Team Durham roster: https://www.notion.so/7e32227adb984542ba5e7b494e951232"
echo "     - Allura Blueprint:   https://www.notion.so/33c1d9be65b38173be9bdb58f13c336e"
echo "     - AD-001:             https://www.notion.so/33e1d9be65b38116a490dbade803c5bd"
echo ""
echo "  Authority direction: Notion → repo (one direction only)"
echo "  Agents read at boot, write to repo and memory, never back to templates."
echo "========================================"