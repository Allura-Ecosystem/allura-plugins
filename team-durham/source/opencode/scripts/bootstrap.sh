#!/bin/bash
# Brand Maker — Harness Bootstrap Script
# Validates .opencode/ structure and checks infrastructure connections
# Usage: bash .opencode/scripts/bootstrap.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "  Brand Maker — Harness Bootstrap"
echo "========================================"
echo ""

ERRORS=0
WARNINGS=0

# ── Agent Definitions ────────────────────────────────────
echo -e "${BLUE}📋 Agent Definitions${NC}"
REQUIRED_AGENTS=(
    "brand_orchestrator"
    "brand_strategist"
    "visual_director"
    "copywriter"
    "brand_kit_builder"
    "qa_reviewer"
    "data_analyst"
    "scout_recon"
    "openagent"
)

for agent in "${REQUIRED_AGENTS[@]}"; do
    if [ -f ".opencode/agent/${agent}/AGENTS.md" ]; then
        echo -e "   ${GREEN}✅${NC} ${agent}"
    else
        echo -e "   ${RED}❌${NC} ${agent} (MISSING)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# ── Skills ───────────────────────────────────────────────
echo -e "${BLUE}🎯 Skills${NC}"
REQUIRED_SKILLS=(
    "brand-consistency-review"
    "brand-strategy"
    "context7"
    "mcp-docker-memory-system"
    "skill-creator"
    "task-management"
)

for skill in "${REQUIRED_SKILLS[@]}"; do
    if [ -f ".opencode/skills/${skill}/SKILL.md" ]; then
        echo -e "   ${GREEN}✅${NC} ${skill}"
    else
        echo -e "   ${RED}❌${NC} ${skill} (MISSING)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# ── Governance Files ──────────────────────────────────────
echo -e "${BLUE}📜 Governance Files${NC}"
REQUIRED_FILES=(
    ".opencode/AGENTS.md"
    ".opencode/AI-GUIDELINES.md"
    ".opencode/HARNESS-GUIDE.md"
    ".opencode/BROOKS-TRACKING.md"
    ".opencode/_bootstrap.md"
    ".opencode/config/agent-metadata.json"
    ".opencode/contracts/harness-v1.md"
    ".opencode/rules/agent-routing.md"
    ".opencode/rules/mcp-integration.md"
    ".opencode/rules/neo4j-best-practices.md"
    ".opencode/rules/postgres-best-practices.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✅${NC} ${file}"
    else
        echo -e "   ${RED}❌${NC} ${file} (MISSING)"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# ── Infrastructure ────────────────────────────────────────
echo -e "${BLUE}🐳 Infrastructure${NC}"

# Check Docker
if command -v docker &> /dev/null; then
    for container in knowledge-postgres knowledge-neo4j allura-memory-mcp; do
        if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
            STATUS=$(docker ps --filter "name=$container" --format '{{.Status}}')
            echo -e "   ${GREEN}✅${NC} $container: $STATUS"
        else
            echo -e "   ${RED}❌${NC} $container: NOT RUNNING"
            WARNINGS=$((WARNINGS + 1))
        fi
    done
else
    echo -e "   ${YELLOW}⚠️${NC}  Docker not found — cannot check containers"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# ── Client Workspaces ────────────────────────────────────
echo -e "${BLUE}📁 Client Workspaces${NC}"
for client_dir in clients/*/; do
    if [[ "$client_dir" == *"_template"* ]]; then
        echo -e "   ${BLUE}📋${NC} $(basename "$client_dir") (template)"
    else
        DELIVERABLES=$(ls "$client_dir"0*.md 2>/dev/null | wc -l)
        echo -e "   ${GREEN}✅${NC} $(basename "$client_dir") ($DELIVERABLES deliverables)"
    fi
done
echo ""

# ── Summary ───────────────────────────────────────────────
echo "========================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "  ${GREEN}✅ Bootstrap: ALL CHECKS PASSED${NC}"
else
    echo -e "  ${RED}❌ Bootstrap: $ERRORS ERROR(S)${NC}"
fi
if [ $WARNINGS -gt 0 ]; then
    echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi
echo "========================================"

exit $ERRORS