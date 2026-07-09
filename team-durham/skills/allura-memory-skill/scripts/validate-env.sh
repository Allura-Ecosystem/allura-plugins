#!/usr/bin/env bash
# validate-env.sh — Verify Allura Brain connectivity before any memory operations
# Usage: ./scripts/validate-env.sh
# Exit codes: 0 = all checks pass, 1 = partial failure, 2 = critical failure

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
WARN=0
FAIL=0

# ─── Check Functions ───

check_docker_running() {
    if ! command -v docker &>/dev/null; then
        echo -e "${RED}FAIL${NC} Docker is not installed or not in PATH"
        ((FAIL++))
        return 1
    fi

    if ! docker info &>/dev/null; then
        echo -e "${RED}FAIL${NC} Docker daemon is not running"
        ((FAIL++))
        return 1
    fi

    echo -e "${GREEN}PASS${NC} Docker daemon is running"
    ((PASS++))
    return 0
}

check_postgres_container() {
    local pg_container
    pg_container=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)

    if [[ -z "$pg_container" ]]; then
        echo -e "${RED}FAIL${NC} No PostgreSQL container running"
        ((FAIL++))
        return 1
    fi

    echo -e "${GREEN}PASS${NC} PostgreSQL container: ${pg_container}"
    ((PASS++))
    return 0
}

check_postgres_connection() {
    local pg_container
    pg_container=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)

    if [[ -z "$pg_container" ]]; then
        echo -e "${YELLOW}SKIP${NC} PostgreSQL connection check (no container)"
        return 0
    fi

    if docker exec "$pg_container" pg_isready -U "${POSTGRES_USER:-ronin4life}" -d "${POSTGRES_DB:-memory}" &>/dev/null; then
        echo -e "${GREEN}PASS${NC} PostgreSQL accepts connections (db: ${POSTGRES_DB:-memory})"
        ((PASS++))
    else
        echo -e "${RED}FAIL${NC} PostgreSQL not accepting connections"
        ((FAIL++))
        return 1
    fi
    return 0
}

check_neo4j_container() {
    local neo4j_container
    neo4j_container=$(docker ps --filter "name=neo4j" --format "{{.Names}}" | head -1)

    if [[ -z "$neo4j_container" ]]; then
        echo -e "${RED}FAIL${NC} No Neo4j container running"
        ((FAIL++))
        return 1
    fi

    echo -e "${GREEN}PASS${NC} Neo4j container: ${neo4j_container}"
    ((PASS++))
    return 0
}

check_neo4j_connection() {
    local neo4j_container
    neo4j_container=$(docker ps --filter "name=neo4j" --format "{{.Names}}" | head -1)

    if [[ -z "$neo4j_container" ]]; then
        echo -e "${YELLOW}SKIP${NC} Neo4j connection check (no container)"
        return 0
    fi

    local neo4j_password="${NEO4J_PASSWORD:-test}"

    if docker exec "$neo4j_container" cypher-shell -u neo4j -p "$neo4j_password" "RETURN 1" &>/dev/null; then
        echo -e "${GREEN}PASS${NC} Neo4j accepts connections"
        ((PASS++))
    else
        echo -e "${YELLOW}WARN${NC} Neo4j connection failed (may need password check)"
        ((WARN++))
    fi
    return 0
}

check_mcp_memory_container() {
    local mcp_container
    mcp_container=$(docker ps --filter "name=allura" --format "{{.Names}}" | head -1)

    if [[ -z "$mcp_container" ]]; then
        echo -e "${YELLOW}WARN${NC} No Allura MCP container running (may use MCP Docker gateway instead)"
        ((WARN++))
        return 0
    fi

    echo -e "${GREEN}PASS${NC} Allura MCP container: ${mcp_container}"
    ((PASS++))
    return 0
}

check_orphan_containers() {
    local orphan_count
    orphan_count=$(docker ps -a --filter "name=allura" --filter "status=exited" --format "{{.Names}}" | wc -l)

    if [[ "$orphan_count" -gt 0 ]]; then
        echo -e "${YELLOW}WARN${NC} Found ${orphan_count} orphan container(s) (exited but not removed)"
        docker ps -a --filter "name=allura" --filter "status=exited" --format "{{.Names}} ({{.Status}})" | while read -r line; do
            echo "       → $line"
        done
        ((WARN++))
    else
        echo -e "${GREEN}PASS${NC} No orphan Allura containers"
        ((PASS++))
    fi
    return 0
}

check_events_table() {
    local pg_container
    pg_container=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)

    if [[ -z "$pg_container" ]]; then
        echo -e "${YELLOW}SKIP${NC} Events table check (no PostgreSQL container)"
        return 0
    fi

    local table_exists
    table_exists=$(docker exec "$pg_container" psql -U "${POSTGRES_USER:-ronin4life}" -d "${POSTGRES_DB:-memory}" -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'events')" 2>/dev/null || echo "false")

    if [[ "$table_exists" == "t" ]]; then
        echo -e "${GREEN}PASS${NC} Events table exists in PostgreSQL"
        ((PASS++))
    else
        echo -e "${YELLOW}WARN${NC} Events table not found in PostgreSQL (may need migration)"
        ((WARN++))
    fi
    return 0
}

check_group_id_constraint() {
    local pg_container
    pg_container=$(docker ps --filter "name=postgres" --format "{{.Names}}" | head -1)

    if [[ -z "$pg_container" ]]; then
        echo -e "${YELLOW}SKIP${NC} Group ID constraint check (no PostgreSQL container)"
        return 0
    fi

    # Try inserting with invalid group_id — should fail
    local result
    result=$(docker exec "$pg_container" psql -U "${POSTGRES_USER:-ronin4life}" -d "${POSTGRES_DB:-memory}" -c "INSERT INTO events (event_type, group_id) VALUES ('VALIDATION_TEST', 'invalid-group')" 2>&1 || true)

    if echo "$result" | grep -qi "check constraint\|violates"; then
        echo -e "${GREEN}PASS${NC} Group ID CHECK constraint is active (rejects invalid patterns)"
        ((PASS++))
    else
        echo -e "${YELLOW}WARN${NC} Group ID CHECK constraint may not be active"
        ((WARN++))

        # Clean up test row if it was inserted
        docker exec "$pg_container" psql -U "${POSTGRES_USER:-ronin4life}" -d "${POSTGRES_DB:-memory}" -c "DELETE FROM events WHERE event_type = 'VALIDATION_TEST'" &>/dev/null || true
    fi
    return 0
}

# ─── Run All Checks ───

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Allura Brain — Environment Validation           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "Layer 1: MCP / Docker Runtime"
echo "─────────────────────────────"
check_docker_running
check_mcp_memory_container
check_orphan_containers
echo ""

echo "Layer 2: Database Connectivity"
echo "──────────────────────────────"
check_postgres_container
check_postgres_connection
check_neo4j_container
check_neo4j_connection
echo ""

echo "Layer 3: Schema & Integrity"
echo "───────────────────────────"
check_events_table
check_group_id_constraint
echo ""

# ─── Summary ───

echo "═══════════════════════════════════════════════════════════"
echo -e "Results: ${GREEN}${PASS} pass${NC}  ${YELLOW}${WARN} warn${NC}  ${RED}${FAIL} fail${NC}"
echo "═══════════════════════════════════════════════════════════"

if [[ $FAIL -gt 0 ]]; then
    echo ""
    echo -e "${RED}CRITICAL: Brain is not fully operational. Fix failures before proceeding.${NC}"
    echo ""
    echo "Quick fixes:"
    echo "  make docker-up     # Restart Docker containers"
    echo "  make db-status     # Check connectivity"
    echo "  docker ps -a       # List all containers"
    exit 2
elif [[ $WARN -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}WARNING: Brain is partially operational. Some checks produced warnings.${NC}"
    echo "Review warnings above before starting memory-intensive operations."
    exit 1
else
    echo ""
    echo -e "${GREEN}ALL CLEAR: Brain is fully operational. Safe to proceed with memory operations.${NC}"
    exit 0
fi