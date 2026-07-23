#!/usr/bin/env bash
# models-eval.sh — CLASSIC eval framework for agent models
#
# Evaluates each agent against canonical fixtures using the CLASSIC framework:
# Cost, Latency, Accuracy, Stability, Security, Intelligence.
# Three-level assessment: end-to-end, trajectory, component.
#
# Usage:
#   bash allura-plugins/scripts/models-eval.sh                    # eval all agents
#   bash allura-plugins/scripts/models-eval.sh brooks             # eval one agent
#   bash allura-plugins/scripts/models-eval.sh --compare last     # compare to previous
#   bash allura-plugins/scripts/models-eval.sh --runtime claude   # one runtime
#
# Exit 0 = all pass (≥85%), Exit 1 = any agent below pass threshold
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REGISTRY="$REPO_ROOT/allura-plugins/docs/models.yaml"
FIXTURES_DIR="$REPO_ROOT/allura-plugins/evals/fixtures"
RESULTS_DIR="$REPO_ROOT/allura-plugins/evals/results"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

FILTER_AGENT=""
COMPARE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --compare) COMPARE="$2"; shift 2 ;;
    *) FILTER_AGENT="$1"; shift ;;
  esac
done

mkdir -p "$RESULTS_DIR"
log() { echo "[models-eval] $*" >&2; }

# ─── Read registry: agent → fixture, primary model ─────────────────
get_agents_with_fixtures() {
  python3 << PYEOF
import yaml, os
with open("$REGISTRY") as f:
    data = yaml.safe_load(f)
agents = data.get('agents', {})
for name, info in agents.items():
    fixture = info.get('eval_fixture', '')
    primary = info.get('primary', '')
    plugin = info.get('plugin', '')
    # fixture path is relative to repo root
    fixture_path = os.path.join("$REPO_ROOT", fixture) if fixture else ''
    if os.path.exists(fixture_path):
        print(f"{name}|{primary}|{fixture_path}|{plugin}")
PYEOF
}

# ─── Run eval for one agent ─────────────────────────────────────────
eval_agent() {
  local agent="$1" model="$2" fixture="$3" plugin="$4"
  local result_file="$RESULTS_DIR/${TIMESTAMP}_${agent}.json"

  log "Evaluating $agent (model: $model, fixture: $(basename "$fixture"))"

  # Read fixture
  local fixture_content
  fixture_content=$(cat "$fixture")

  # ─── Simulate eval (real implementation would invoke the agent) ───
  # In production, this would:
  # 1. Invoke the agent with the fixture task
  # 2. Measure TTFT + end-to-end latency
  # 3. Count tokens (input + output)
  # 4. Run the agent's own validation gate (accuracy)
  # 5. Run N times for stability
  # 6. Run Allura governance gates (security)
  # 7. LLM-as-judge on reasoning trace (intelligence)
  #
  # For now, we record the fixture + model + timestamp as a placeholder
  # and compute cost from the registry.

  local cost_input cost_output
  cost_input=$(python3 -c "
import yaml
with open('$REGISTRY') as f:
    d = yaml.safe_load(f)
m = d.get('models', {}).get('$model', {})
print(m.get('cost_per_1m_input', 0))
" 2>/dev/null)
  cost_output=$(python3 -c "
import yaml
with open('$REGISTRY') as f:
    d = yaml.safe_load(f)
m = d.get('models', {}).get('$model', {})
print(m.get('cost_per_1m_output', 0))
" 2>/dev/null)

  # Write result JSON
  python3 -c "
import json, time
result = {
    'agent': '$agent',
    'model': '$model',
    'plugin': '$plugin',
    'fixture': '$fixture',
    'timestamp': '$TIMESTAMP',
    'metrics': {
        'cost': {
            'cost_per_1m_input': $cost_input,
            'cost_per_1m_output': $cost_output,
            'estimated_input_tokens': 0,
            'estimated_output_tokens': 0,
            'estimated_cost_usd': 0
        },
        'latency': {
            'ttft_ms': 0,
            'e2e_ms': 0,
            'profile': 'unknown'
        },
        'accuracy': {
            'task_completed': False,
            'validation_gate_passed': False,
            'score': 0.0
        },
        'stability': {
            'runs': 0,
            'success_rate': 0.0,
            'variance': 0.0
        },
        'security': {
            'governance_gates_passed': 0,
            'governance_gates_total': 6,
            'violations': []
        },
        'intelligence': {
            'llm_judge_score': 0.0,
            'reasoning_quality': 'unknown'
        }
    },
    'overall_score': 0.0,
    'pass_threshold': 0.85,
    'ship_threshold': 0.90,
    'status': 'fixture-recorded',
    'note': 'Placeholder result. Real eval requires agent invocation + Brain trace analysis.'
}
with open('$result_file', 'w') as f:
    json.dump(result, f, indent=2)
print('written')
" 2>/dev/null

  echo "$result_file"
}

# ─── Compare to previous run ────────────────────────────────────────
compare_results() {
  local current="$1" previous="$2"
  python3 -c "
import json
with open('$current') as f: c = json.load(f)
with open('$previous') as f: p = json.load(f)
print(f'Agent: {c[\"agent\"]}')
print(f'Model: {c[\"model\"]}')
print(f'Previous score: {p.get(\"overall_score\", 0):.2f}')
print(f'Current score:  {c.get(\"overall_score\", 0):.2f}')
delta = c.get('overall_score', 0) - p.get('overall_score', 0)
print(f'Delta: {delta:+.2f} {\"✅ improved\" if delta > 0 else \"❌ regressed\" if delta < 0 else \"→ no change\"}')
" 2>/dev/null
}

# ─── Main ───────────────────────────────────────────────────────────
log "Loading registry from $REGISTRY"
log "Fixtures dir: $FIXTURES_DIR"
log "Results dir: $RESULTS_DIR"

AGENTS_DATA=$(get_agents_with_fixtures)
FIXTURE_COUNT=$(echo "$AGENTS_DATA" | grep -c . || true)
FIXTURE_COUNT=${FIXTURE_COUNT//[^0-9]/}
FIXTURE_COUNT=${FIXTURE_COUNT:-0}

if [[ $FIXTURE_COUNT -eq 0 ]]; then
  log "No eval fixtures found. Create fixtures in $FIXTURES_DIR/"
  log "See Phase 5 of the model governance plan."
  exit 0
fi

log "Found $FIXTURE_COUNT agents with fixtures"

declare -a RESULTS
ANY_FAIL=0

while IFS='|' read -r agent model fixture plugin; do
  [[ -z "$agent" ]] && continue
  if [[ -n "$FILTER_AGENT" && "$agent" != "$FILTER_AGENT" ]]; then continue; fi

  result_file=$(eval_agent "$agent" "$model" "$fixture" "$plugin")

  # Compare if requested
  if [[ -n "$COMPARE" ]]; then
    # Find previous result
    previous=$(ls -t "$RESULTS_DIR"/*_"$agent".json 2>/dev/null | grep -v "$TIMESTAMP" | head -1)
    if [[ -n "$previous" ]]; then
      compare_results "$result_file" "$previous"
    fi
  fi

  RESULTS+=("$agent|$model|fixture-recorded")
done <<< "$AGENTS_DATA"

# Print summary
echo ""
echo "EVAL SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo "AGENT               MODEL                  STATUS"
echo "─────────────────── ────────────────────── ──────────────────"
for row in "${RESULTS[@]}"; do
  IFS='|' read -r agent model status <<< "$row"
  printf "%-19s %-22s %s\n" "$agent" "$model" "$status"
done

echo ""
log "Eval complete. Results in $RESULTS_DIR"
log "Note: Results are placeholders. Real eval requires agent invocation."
log "Run models-performance.sh for live metrics from Brain traces."

exit $ANY_FAIL