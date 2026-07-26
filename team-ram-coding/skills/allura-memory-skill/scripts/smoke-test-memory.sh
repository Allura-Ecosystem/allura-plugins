#!/bin/bash
# smoke-test-memory.sh — Quick smoke test for Allura Brain memory operations
# Uses direct Docker access for health checks; for memory operations, use MCP tools: allura-brain_memory_*

set -e

echo "=== Allura Brain Smoke Test ==="

# Test PostgreSQL
echo "Testing PostgreSQL..."
PG_COUNT=$(docker exec knowledge-postgres psql -U ronin4life -d memory -t -c "SELECT count(*) FROM allura_memories;" 2>/dev/null | tr -d ' ' || echo "unavailable")
echo "  PG memories: $PG_COUNT"

# Test semantic graph
# Probed through the governed gateway, not a database driver. No credential lives
# in this file — the previous version embedded one in plaintext and, under `set -e`,
# aborted the script here so every check below never ran.
echo "Testing semantic graph..."
GATEWAY="${ALLURA_GATEWAY_URL:-http://localhost:5888}"
if curl -fsS --max-time 5 "${GATEWAY}/health" 2>/dev/null | grep -qi "ok\|ready\|healthy\|degraded"; then
  echo "  ✅ semantic graph gateway responding (${GATEWAY})"
else
  echo "  ⚠️  semantic graph gateway not responding (${GATEWAY})"
fi

# Test Ollama
echo "Testing Ollama..."
if curl -s http://localhost:11434/api/tags | grep -q qwen3; then
  echo "  ✅ qwen3-embedding:8b available"
else
  echo "  ❌ qwen3-embedding:8b not found in Ollama"
fi

# Test MCP server (if accessible)
echo "Testing MCP HTTP gateway..."
if curl -s http://localhost:3201/ready 2>/dev/null | grep -q "ok\|ready\|healthy"; then
  echo "  ✅ HTTP gateway responding"
else
  echo "  ⚠️  HTTP gateway not responding (may not be mapped to host)"
fi

echo ""
echo "=== Done ==="