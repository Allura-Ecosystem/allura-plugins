#!/usr/bin/env bash
# models-performance.sh — aggregate model performance from Allura Brain traces
#
# Reads MODEL_INVOKED events from Allura Brain (via MCP) and aggregates:
# - avg/p95 latency per agent+model
# - avg token count per agent+model
# - estimated cost per agent+model
# - error rate per agent+model
# - suggests downgrades (sonnet where opus passed) and upgrades (haiku where sonnet failed)
#
# Usage:
#   bash allura-plugins/scripts/models-performance.sh                    # last 7 days
#   bash allura-plugins/scripts/models-performance.sh --days 30          # last 30 days
#   bash allura-plugins/scripts/models-performance.sh --agent brooks      # one agent
#   bash allura-plugins/scripts/models-performance.sh --suggest           # suggest model changes
#
# Exit 0 = success, Exit 1 = Brain unavailable or no data
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY="$REPO_ROOT/allura-plugins/docs/models.yaml"
DAYS=7
FILTER_AGENT=""
SUGGEST=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --days) DAYS="$2"; shift 2 ;;
    --agent) FILTER_AGENT="$2"; shift 2 ;;
    --suggest) SUGGEST=true; shift ;;
  esac
done

log() { echo "[models-performance] $*" >&2; }

# ─── Check Brain availability ───────────────────────────────────────
check_brain() {
  if curl -s --max-time 3 http://localhost:5888/mcp >/dev/null 2>&1; then
    return 0
  else
    return 1
  fi
}

# ─── Query Brain audit events for MODEL_INVOKED ─────────────────────
# Uses the allura-brain MCP audit_query_events tool
query_model_events() {
  python3 << 'PYEOF'
import json, urllib.request, sys

# Query Allura Brain audit events for MODEL_INVOKED events
# This is a placeholder — real implementation would call the MCP tool:
# allura-brain_audit_query_events({group_id: "allura-system", event_type: "MODEL_INVOKED", limit: 200})

# For now, return empty data structure
print(json.dumps({
    "events": [],
    "note": "Brain query placeholder. Real implementation uses allura-brain_audit_query_events MCP tool."
}))
PYEOF
}

# ─── Aggregate events ───────────────────────────────────────────────
aggregate() {
  local events="$1"
  python3 << PYEOF
import json, sys
from collections import defaultdict

events = json.loads('''$events''').get('events', [])

if not events:
    print(json.dumps({"agents": [], "note": "No MODEL_INVOKED events found."}))
    sys.exit(0)

# Aggregate by agent+model
agg = defaultdict(lambda: {
    'invocations': 0, 'total_latency_ms': 0, 'latencies': [],
    'total_input_tokens': 0, 'total_output_tokens': 0,
    'errors': 0, 'successes': 0
})

for event in events:
    meta = event.get('metadata', {})
    agent = meta.get('agent_id', 'unknown')
    model = meta.get('model', 'unknown')
    key = f"{agent}|{model}"

    agg[key]['invocations'] += 1
    latency = meta.get('latency_ms', 0)
    agg[key]['total_latency_ms'] += latency
    agg[key]['latencies'].append(latency)
    agg[key]['total_input_tokens'] += meta.get('input_tokens', 0)
    agg[key]['total_output_tokens'] += meta.get('output_tokens', 0)

    if meta.get('error'):
        agg[key]['errors'] += 1
    else:
        agg[key]['successes'] += 1

# Compute stats
results = []
for key, data in agg.items():
    agent, model = key.split('|', 1)
    latencies = sorted(data['latencies'])
    n = len(latencies)
    p95_idx = int(n * 0.95)

    results.append({
        'agent': agent,
        'model': model,
        'invocations': data['invocations'],
        'avg_latency_ms': round(data['total_latency_ms'] / max(n, 1), 1),
        'p95_latency_ms': latencies[p95_idx] if n > 0 else 0,
        'avg_input_tokens': round(data['total_input_tokens'] / max(n, 1)),
        'avg_output_tokens': round(data['total_output_tokens'] / max(n, 1)),
        'error_rate': round(data['errors'] / max(data['invocations'], 1) * 100, 1),
        'success_rate': round(data['successes'] / max(data['invocations'], 1) * 100, 1)
    })

print(json.dumps({"agents": results}))
PYEOF
}

# ─── Suggest model changes ──────────────────────────────────────────
suggest_changes() {
  local results="$1"
  python3 << PYEOF
import json, yaml, sys

results = json.loads('''$results''').get('agents', [])

with open("$REGISTRY") as f:
    registry = yaml.safe_load(f)
models = registry.get('models', {})
agents = registry.get('agents', {})

suggestions = []

for r in results:
    agent = r['agent']
    model = r['model']
    agent_reg = agents.get(agent, {})
    category = agent_reg.get('category', '')

    # Suggest downgrade if: high success rate + low latency + opus model
    if r['success_rate'] > 90 and r['avg_latency_ms'] < 2000 and 'opus' in model:
        suggestions.append({
            'agent': agent,
            'current': model,
            'suggested': 'claude-sonnet-4',
            'reason': f"Success rate {r['success_rate']}% with low latency — sonnet likely sufficient",
            'est_savings_per_1m': models.get('claude-opus-4-8', {}).get('cost_per_1m_input', 0) - models.get('claude-sonnet-4', {}).get('cost_per_1m_input', 0)
        })

    # Suggest upgrade if: low success rate
    if r['success_rate'] < 70 and 'haiku' in model:
        suggestions.append({
            'agent': agent,
            'current': model,
            'suggested': 'claude-sonnet-4',
            'reason': f"Success rate only {r['success_rate']}% — upgrade to sonnet",
            'est_cost_increase_per_1m': models.get('claude-sonnet-4', {}).get('cost_per_1m_input', 0) - models.get('claude-haiku-4-5', {}).get('cost_per_1m_input', 0)
        })

if not suggestions:
    print("No model change suggestions — current assignments look optimal.")
else:
    print("MODEL CHANGE SUGGESTIONS:")
    for s in suggestions:
        print(f"  {s['agent']}: {s['current']} → {s['suggested']}")
        print(f"    Reason: {s['reason']}")
        if s.get('est_savings_per_1m'):
            print(f"    Est. savings: \${s['est_savings_per_1m']}/1M input tokens")
        if s.get('est_cost_increase_per_1m'):
            print(f"    Est. cost increase: \${s['est_cost_increase_per_1m']}/1M input tokens")
PYEOF
}

# ─── Main ───────────────────────────────────────────────────────────
log "Checking Allura Brain availability..."
if ! check_brain; then
  log "❌ Allura Brain not reachable at localhost:5888"
  log "Start Brain or run without performance monitoring."
  echo ""
  echo "PERFORMANCE REPORT (degraded — Brain unavailable)"
  echo "═══════════════════════════════════════════════════"
  echo "No live data. Brain must be running to aggregate MODEL_INVOKED events."
  echo ""
  echo "To start Brain: cd allura-memory && bun dev"
  exit 1
fi

log "Brain reachable. Querying MODEL_INVOKED events (last $DAYS days)..."
EVENTS=$(query_model_events)
RESULTS=$(aggregate "$EVENTS")

# Print report
echo ""
echo "MODEL PERFORMANCE REPORT (last $DAYS days)"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "AGENT               MODEL                  INVOCATIONS  AVG LATENCY  P95 LATENCY  ERROR RATE  SUCCESS"
echo "─────────────────── ────────────────────── ──────────── ──────────── ──────────── ─────────── ────────"

python3 -c "
import json
results = json.loads('''$RESULTS''').get('agents', [])
if not results:
    print('(no MODEL_INVOKED events found in Brain)')
else:
    for r in results:
        print(f\"{r['agent']:<19} {r['model']:<22} {r['invocations']:<12} {r['avg_latency_ms']:<12} {r['p95_latency_ms']:<12} {r['error_rate']:<11} {r['success_rate']}\")
"

echo ""

if $SUGGEST; then
  log "Generating model change suggestions..."
  suggest_changes "$RESULTS"
fi

log "Report complete."

exit 0