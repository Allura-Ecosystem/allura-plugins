# Hybrid Model Routing Implementation Plan

> **STATUS: SUPERSEDED by AD-004 (2026-08-17).** Pike review determined that the harness configs are the enforcement point, not a separate `contracts.json` registry. The four-task plan below is retained for reference but is no longer the execution path. The actual fix was applied directly to `~/.config/opencode/opencode.json` and `~/.config/openwork/runtime-opencode-config.json`.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Team RAM Coding and Team Durham use the approved five-contract Codex/Ollama routing policy, with deterministic escalation and auditable Allura receipts.

**Architecture:** Store a provider-neutral routing registry in the plugin monorepo and make every agent declaration refer to a named contract. A small Node validator verifies that assignments are complete, only approved models occur, and stale defaults are absent. Runtime adapters select the assigned model; Allura records the resulting route and validation evidence without altering policy.

**Tech Stack:** JSON, Markdown front matter, Node.js built-in `node:assert`/`node:fs`, Codex, Ollama Cloud, Allura Brain.

**Spec:** `team-durham/docs/superpowers/specs/2026-08-16-hybrid-model-routing-design.md`

## Global Constraints

- Use exactly these contracts: `architecture`, `routine_coding`, `general`, `vision`, and `embeddings`.
- Codex `gpt-5.6-terra` is required for architecture/final-judgment work.
- Ollama Cloud `kimi-k2.7-code:cloud`, `glm-5.2:cloud`, and `qwen3.5:397b-cloud` are the only automatic non-embedding defaults.
- `qwen3-embedding:8b` is retrieval-only.
- No automatic route change may be inferred from model self-confidence or raw Allura traces.
- Team Durham memory writes use `allura-team-durham`; obtain an authorized principal before enabling its event emitter.

---

## File Structure

| File | Responsibility |
| --- | --- |
| `model-routing/contracts.json` | Single source of truth for contract names, models, task classes, and escalation conditions. |
| `scripts/validate-model-routing.mjs` | Validates registry shape and every mapped agent assignment. |
| `scripts/validate-model-routing.test.mjs` | Exercises valid, stale-model, and incomplete-assignment cases. |
| `team-ram-coding/agents/*.md` | Declares each coding specialist's `model_contract`; preserves runtime-specific Claude aliases until the adapter consumes the contract. |
| `team-durham/agents/*.md` | Updates explicit `## Model & Routing` declarations and adds `model_contract` front matter. |
| `team-durham/docs/AGENTS.md` | Replaces the obsolete GLM 5.1 routing summary with the canonical-contract reference. |
| `team-ram-coding/commands/start-session.md`, `team-durham/commands/start-session.md` | Requires route selection and an evidence receipt at session start/close. |

### Task 1: Add the canonical routing registry and validator

**Files:**
- Create: `model-routing/contracts.json`
- Create: `scripts/validate-model-routing.mjs`
- Create: `scripts/validate-model-routing.test.mjs`

**Interfaces:**
- Consumes: agent mapping objects of shape `{ agent, plugin, contract }`.
- Produces: exit status `0` only when every assigned contract exists, every model is approved, and every required agent occurs exactly once.

- [ ] **Step 1: Write the failing validator test**

```js
import assert from 'node:assert/strict';
import { validateRegistry } from './validate-model-routing.mjs';

assert.throws(
  () => validateRegistry({ contracts: {}, assignments: [] }),
  /missing required contract: architecture/
);
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node scripts/validate-model-routing.test.mjs`

Expected: failure because `validate-model-routing.mjs` does not exist.

- [ ] **Step 3: Create the minimal registry**

```json
{
  "schema_version": 1,
  "contracts": {
    "architecture": { "provider": "codex", "model": "gpt-5.6-terra" },
    "routine_coding": { "provider": "ollama-cloud", "model": "kimi-k2.7-code:cloud" },
    "general": { "provider": "ollama-cloud", "model": "glm-5.2:cloud" },
    "vision": { "provider": "ollama-cloud", "model": "qwen3.5:397b-cloud" },
    "embeddings": { "provider": "ollama", "model": "qwen3-embedding:8b" }
  },
  "escalate_to_architecture_on": ["provider_unavailable", "malformed_tool_output", "quality_gate_failure", "second_validation_failure"],
  "assignments": []
}
```

- [ ] **Step 4: Implement the validator**

```js
import assert from 'node:assert/strict';

export function validateRegistry(registry) {
  for (const name of ['architecture', 'routine_coding', 'general', 'vision', 'embeddings']) {
    assert.ok(registry.contracts?.[name], `missing required contract: ${name}`);
  }
  const seen = new Set();
  for (const assignment of registry.assignments) {
    assert.ok(registry.contracts[assignment.contract], `unknown contract: ${assignment.contract}`);
    const key = `${assignment.plugin}/${assignment.agent}`;
    assert.ok(!seen.has(key), `duplicate assignment: ${key}`);
    seen.add(key);
  }
}
```

- [ ] **Step 5: Run the test and registry check**

Run: `node scripts/validate-model-routing.test.mjs && node scripts/validate-model-routing.mjs model-routing/contracts.json`

Expected: both commands exit `0`.

- [ ] **Step 6: Commit**

```bash
git add model-routing/contracts.json scripts/validate-model-routing.mjs scripts/validate-model-routing.test.mjs
git commit -m "feat: add canonical model routing registry"
```

### Task 2: Map Team RAM Coding agents to the contracts

**Files:**
- Modify: `team-ram-coding/agents/brooks.md`, `jobs.md`, `hightower.md`, `fowler.md`, `pike.md`, `knuth.md`, `bellard.md`, `carmack.md`, `woz.md`, `scout.md`, `bahari.md`
- Modify: `model-routing/contracts.json`
- Test: `scripts/validate-model-routing.test.mjs`

**Interfaces:**
- Consumes: the five canonical contracts from Task 1.
- Produces: exactly one registry assignment and `model_contract` front-matter property per Team RAM agent.

- [ ] **Step 1: Add failing completeness assertion**

```js
assert.throws(
  () => validateRegistry({ contracts: validContracts, assignments: [{ plugin: 'team-ram-coding', agent: 'brooks', contract: 'architecture' }] }),
  /missing assignment: team-ram-coding\/woz/
);
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node scripts/validate-model-routing.test.mjs`

Expected: failure reporting the missing Woz assignment.

- [ ] **Step 3: Add assignments and matching front matter**

Assign Brooks, Jobs, Hightower, Fowler, Pike, Knuth, Bellard, and Bahari to `architecture`; assign Woz and Carmack to `routine_coding`; assign Scout to `general`. Add, for example, directly after `model:` in `team-ram-coding/agents/brooks.md`:

```yaml
model_contract: architecture
```

- [ ] **Step 4: Extend validator to require all Team RAM agents**

```js
const required = ['brooks', 'jobs', 'hightower', 'fowler', 'pike', 'knuth', 'bellard', 'bahari', 'woz', 'carmack', 'scout'];
for (const agent of required) {
  assert.ok(seen.has(`team-ram-coding/${agent}`), `missing assignment: team-ram-coding/${agent}`);
}
```

- [ ] **Step 5: Verify**

Run: `node scripts/validate-model-routing.test.mjs && node scripts/validate-model-routing.mjs model-routing/contracts.json`

Expected: exit `0`; no Team RAM agent has more than one assignment.

- [ ] **Step 6: Commit**

```bash
git add model-routing/contracts.json team-ram-coding/agents scripts/validate-model-routing.mjs scripts/validate-model-routing.test.mjs
git commit -m "feat: route team ram agents by contract"
```

### Task 3: Map Team Durham agents and remove stale defaults

**Files:**
- Modify: `team-durham/agents/workflow-architect.md`, `reality-checker.md`, `brand-orchestrator.md`, `agentic-trust-architect.md`
- Modify: `team-durham/agents/copywriter.md`, `evidence-collector.md`, `openagent.md`, `data-analyst.md`
- Modify: `team-durham/agents/visual-director.md`, `qa-reviewer.md`, `brand-kit-builder.md`, `scout-recon.md`, `brand-strategist.md`
- Modify: `team-durham/docs/AGENTS.md`, `model-routing/contracts.json`
- Test: `scripts/validate-model-routing.test.mjs`

**Interfaces:**
- Consumes: approved registry contracts.
- Produces: Team Durham routing declarations matching the registry and no automatic use of GLM 5.1, Kimi 2.5/2.6, or Gemma 31B.

- [ ] **Step 1: Write stale-default assertions**

```js
for (const stale of ['glm-5.1', 'kimi-k2.5', 'kimi-k2.6', 'gemma4:31b']) {
  assert.doesNotMatch(renderedAgentText, new RegExp(stale));
}
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node scripts/validate-model-routing.test.mjs`

Expected: failure naming at least `glm-5.1`.

- [ ] **Step 3: Apply the approved Team Durham assignments**

Use `architecture` for Workflow Architect, Reality Checker, Brand Orchestrator, and Agentic Trust Architect; `general` for Copywriter, Evidence Collector, OpenAgent, and Data Analyst; `vision` for Visual Director, QA Reviewer, Brand Kit Builder, Scout Recon, and Brand Strategist. For each, add `model_contract: <contract>` to front matter and replace its explicit `**Model:**` routing statement with the matching canonical provider/model.

- [ ] **Step 4: Update the project guidance**

Replace the `docs/AGENTS.md` statement that text-only agents use GLM 5.1 with:

```markdown
Model routing is defined by `model-routing/contracts.json`. Text specialists use the `general` contract; vision-critical agents use `vision`; architecture, security, data, final-review, and release decisions use `architecture`.
```

- [ ] **Step 5: Verify all declarations**

Run: `node scripts/validate-model-routing.test.mjs && node scripts/validate-model-routing.mjs model-routing/contracts.json && rg -n "glm-5\.1|kimi-k2\.5|kimi-k2\.6|gemma4:31b" team-durham/agents team-durham/docs/AGENTS.md`

Expected: the Node commands exit `0`; `rg` returns no matches.

- [ ] **Step 6: Commit**

```bash
git add model-routing/contracts.json team-durham/agents team-durham/docs/AGENTS.md scripts/validate-model-routing.mjs scripts/validate-model-routing.test.mjs
git commit -m "feat: align team durham model routing"
```

### Task 4: Add route evidence requirements to session contracts

**Files:**
- Modify: `team-ram-coding/commands/start-session.md`
- Modify: `team-durham/commands/start-session.md`
- Modify: `scripts/validate-model-routing.mjs`
- Test: `scripts/validate-model-routing.test.mjs`

**Interfaces:**
- Consumes: selected `model_contract`, provider/model, task class, and validation evidence.
- Produces: an append-only Allura event payload; no policy mutation.

- [ ] **Step 1: Write failing documentation-contract test**

```js
assert.match(teamRamStartSession, /model_contract.*provider.*validation evidence/s);
assert.match(teamDurhamStartSession, /allura-team-durham/);
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `node scripts/validate-model-routing.test.mjs`

Expected: failure because the required evidence fields are absent.

- [ ] **Step 3: Add the required route receipt template to both session commands**

```text
Route receipt: task_class, model_contract, provider, model, fallback_reason?, latency_ms?, validation_evidence, outcome.
Write it as an append-only episodic event. Do not change model_contract from a raw outcome; route changes require explicit approval.
```

In Team Durham’s command, require `group_id: allura-team-durham` and stop with a visible authorization warning if the principal is unauthorized.

- [ ] **Step 4: Add validator checks for the receipt template**

```js
for (const field of ['task_class', 'model_contract', 'provider', 'model', 'validation_evidence', 'outcome']) {
  assert.match(commandText, new RegExp(field));
}
```

- [ ] **Step 5: Verify**

Run: `node scripts/validate-model-routing.test.mjs && node scripts/validate-model-routing.mjs model-routing/contracts.json`

Expected: exit `0` and no live provider call is required.

- [ ] **Step 6: Commit**

```bash
git add team-ram-coding/commands/start-session.md team-durham/commands/start-session.md scripts/validate-model-routing.mjs scripts/validate-model-routing.test.mjs
git commit -m "feat: record routed task evidence"
```

## Self-Review

- **Spec coverage:** Tasks 1–3 implement the five contracts and complete agent mapping; Task 4 implements deterministic evidence capture and preserves human governance. Escalation conditions are encoded in the registry in Task 1.
- **Placeholder scan:** No TBD/TODO items or unspecified file paths remain.
- **Consistency:** All tasks use the same five contract names and exact model identifiers defined in the specification.

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-08-16-hybrid-model-routing.md`.

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task and review between tasks.
2. **Inline Execution** — execute tasks in this session with checkpoints.
