# Plugin Catalog and Hermes Delivery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the remaining P-1 catalog-release and P-2 Hermes-provider stories with reproducible validation and an evidence-backed release gate.

**Architecture:** Keep runtime adapters separate: Claude/Codex remain package-manifest surfaces, OpenCode is represented by an explicit export contract, and Hermes remains a native provider declared by `plugin.yaml`. Shared scripts validate catalog invariants; the Hermes provider validates inputs, obtains tenant scope from trusted initialization context, and returns explicit degraded results after bounded retries.

**Tech Stack:** Python 3, pytest, GitHub Actions, JSON manifests, YAML provider manifest, Markdown skill metadata.

**Spec:** `_bmad/bmm/planning/plugins/epic-p-1-plugin-catalog-release.md`, `_bmad/bmm/planning/plugins/epic-p-2-hermes-brain-connector.md`, and `_bmad/bmm/stories/p-1-*.md`, `_bmad/bmm/stories/p-2-*.md`.

## Global Constraints

- Preserve existing dirty-worktree changes; stage only files owned by a completed story.
- Python dependencies required by tests must be declared and installed by CI; do not rely on host-local packages.
- Hermes tenant scope is trusted initialization context; tool-call arguments must not override it.
- Never expose curator or governance mutation operations through the Hermes provider.
- CI must validate behavior, not merely parse source text.
- All Allura traces use `group_id: allura-system`; semantic promotion remains HITL-only.

---

## File Structure

- `scripts/validate_manifests.py` — catalog and native-manifest structural validation.
- `scripts/validate_evals.py` — deterministic fixture inventory and result-schema validation.
- `scripts/sync_runtime_surfaces.py` — emits machine-readable Claude/Codex/OpenCode drift report.
- `scripts/validate_skill_dependencies.py` — validates required dependency metadata and produces absent-service fixtures.
- `plugins/hermes-allura-brain/contracts.py` — typed provider request/result/error and trusted context models.
- `plugins/hermes-allura-brain/client.py` — bounded retry and normalized degraded-state transport behavior.
- `plugins/hermes-allura-brain/__init__.py` — thin provider dispatch; no caller-controlled tenant scope.
- `requirements-dev.txt` — pytest, PyYAML, MCP SDK, and Hermes runtime test dependency source.
- `tests/` — real behavior tests for catalog scripts and Hermes contracts.
- `.github/workflows/ci.yml` — installs Python test dependencies and runs the release evidence lanes.

### Task 1: P-1.2 — Deterministic eval-fixture coverage

**Files:**
- Create: `scripts/validate_evals.py`, `tests/test_validate_evals.py`
- Modify: `docs/models.yaml`, `scripts/models-eval.sh`, `.github/workflows/ci.yml`
- Create: missing files referenced by `eval_fixture` in `docs/models.yaml` under `evals/fixtures/`

**Interfaces:**
- Produces `validate_evals.main() -> int`, which exits non-zero if any registry agent lacks a fixture or a fixture/result fails the documented schema.
- Produces `evals/results/<agent>.json` with `agent_id`, `fixture`, `verdict`, `evaluator_version`, and `evidence`.

- [ ] Write a failing pytest case with a temporary models registry declaring a missing fixture; assert `validate_evals` returns `1` and names that file.
- [ ] Run `python3 -m pytest tests/test_validate_evals.py -q`; confirm the missing validator fails.
- [ ] Implement registry parsing and fixture/result validation with deterministic local verdicts (`pass` or `fail` only; no synthetic model-execution claim).
- [ ] Add every missing registry fixture, each with a stable scenario, expected behavioral assertions, and no secrets.
- [ ] Update `models-eval.sh` to call `validate_evals.py` and fail when any fixture is absent.
- [ ] Re-run the focused pytest and `bash scripts/models-eval.sh`; confirm coverage output names every registry agent.
- [ ] Commit the story-owned files with `test: validate complete catalog eval fixture coverage`.

### Task 2: P-1.3 — Runtime export contract and drift detection

**Files:**
- Create: `scripts/sync_runtime_surfaces.py`, `tests/test_sync_runtime_surfaces.py`, `runtime-surfaces.json`
- Modify: `README.md`, `.github/workflows/ci.yml`, `docs/RISKS-AND-DECISIONS.md`

**Interfaces:**
- `scripts/sync_runtime_surfaces.py --check` exits `0` only when the generated report contains no unintended drift.
- `runtime-surfaces.json` is the explicit OpenCode export contract, mapping package name to agents, commands, skills, version, and intentional runtime differences.

- [ ] Write a failing test with Claude and Codex manifests whose declared command sets differ without an allow-listed exception; assert the report has `status: "drift"` and the exact missing command.
- [ ] Run the focused test and confirm failure before the sync script exists.
- [ ] Implement manifest collection, the explicit OpenCode contract reader, and JSON report generation; treat declared capability differences as valid only when documented in `runtime-surfaces.json`.
- [ ] Add `runtime-surfaces.json` for all three catalog packages; record current intentional differences such as Claude-only agent lists.
- [ ] Add `--check` to CI and document the local command in the README.
- [ ] Run `python3 scripts/sync_runtime_surfaces.py --check` and its focused pytest.
- [ ] Commit the story-owned files with `feat: add catalog runtime surface drift checks`.

### Task 3: P-1.4 — Dependency metadata and visible degradation

**Files:**
- Create: `scripts/validate_skill_dependencies.py`, `tests/test_validate_skill_dependencies.py`, `docs/SKILL-DEPENDENCY-CONTRACT.md`
- Modify: selected skill frontmatter and package READMEs; `.github/workflows/ci.yml`

**Interfaces:**
- Every `SKILL.md` declares `dependencies` as an empty list or objects of shape `{ "name": string, "required": boolean, "degraded_message": string }`.
- `validate_skill_dependencies.py --check` fails on malformed metadata and `--simulate-missing <name>` prints the declared degraded message and exits `0`.

- [ ] Write a failing test for a skill lacking dependency metadata and a second test for a malformed degraded message.
- [ ] Run the focused test and confirm the validator fails.
- [ ] Implement metadata parsing; start with every existing `SKILL.md`, classifying only externally required services as `required: true` and optional integrations as `required: false`.
- [ ] Add the dependency contract document and update package READMEs with the no-op behavior.
- [ ] Add CI validation and representative absent-service simulations for MCP Docker, Figma, Penpot, and Hermes dependencies.
- [ ] Run focused tests and `python3 scripts/validate_skill_dependencies.py --check`.
- [ ] Commit the story-owned files with `feat: declare skill dependencies and degraded behavior`.

### Task 4: P-2.1 — Typed Hermes provider contract

**Files:**
- Create: `plugins/hermes-allura-brain/contracts.py`, `tests/test_hermes_contracts.py`
- Modify: `plugins/hermes-allura-brain/__init__.py`, `plugins/hermes-allura-brain/README.md`, `requirements-dev.txt`

**Interfaces:**
- `RecallRequest(query: str, limit: int = 5, min_score: float | None = None)` validates non-empty query, `1 <= limit <= 50`, and score range `0..1`.
- `RememberRequest(content: str, metadata: dict[str, str])` validates non-empty bounded content and disallows identity/scope override keys.
- `ProviderResult(ok: bool, data: dict, error: ProviderError | None, degraded: bool)` is the only provider response envelope.

- [ ] Write failing contract tests for empty query, limit `0`, score `1.1`, empty content, and a metadata `group_id` override.
- [ ] Run `python3 -m pytest tests/test_hermes_contracts.py -q` in the declared dependency environment; confirm failures.
- [ ] Implement the typed contract models and convert `allura_recall` and `allura_remember` dispatch to use them.
- [ ] Remove `allura_governance_check` from exposed tool schemas and dispatch.
- [ ] Update README examples to show only recall and remember envelopes.
- [ ] Re-run contract tests plus existing Hermes tests in the declared environment.
- [ ] Commit the story-owned files with `feat: type Hermes memory provider contract`.

### Task 5: P-2.2 — Trusted tenant inheritance

**Files:**
- Modify: `plugins/hermes-allura-brain/contracts.py`, `plugins/hermes-allura-brain/__init__.py`, `plugins/hermes-allura-brain/cli.py`, `tests/test_hermes_contracts.py`, `tests/test_hermes_allura_brain.py`

**Interfaces:**
- `DelegationContext(group_id: str, agent_id: str, parent_session_id: str)` is required at initialization.
- Tool calls use `provider.context.group_id`; caller arguments and metadata may not provide `group_id` or `user_id`.
- Tenant mismatch returns `ProviderResult(ok=False, error=ProviderError(code="TENANT_FORGERY"), degraded=False)` and writes a sanitized audit log.

- [ ] Write failing tests proving a child inherits `allura-faithmeats`, rejects `allura-difference-driven`, and rejects missing trusted context.
- [ ] Run the focused tests and confirm the current defaulting/caller-override behavior fails them.
- [ ] Implement context validation at initialization and remove `_validate_group_id(None)` fallback behavior.
- [ ] Pass only trusted identity and tenant fields to client calls; redact rejected values in logs.
- [ ] Re-run all Hermes contract and behavior tests using the declared dependency environment.
- [ ] Commit the story-owned files with `feat: enforce Hermes delegated tenant scope`.

### Task 6: P-2.3 — Bounded retry and degraded response

**Files:**
- Modify: `plugins/hermes-allura-brain/client.py`, `plugins/hermes-allura-brain/contracts.py`, `plugins/hermes-allura-brain/__init__.py`, `tests/test_hermes_contracts.py`, `tests/test_hermes_allura_brain.py`

**Interfaces:**
- `AlluraBrainClient.call_tool(...) -> ProviderResult` retries retryable transport failures at most `max_retries` times with exponential backoff.
- Exhaustion returns `ProviderResult(ok=False, degraded=True, error=ProviderError(code="BRAIN_UNAVAILABLE"))`.
- Read-only recall returns a clear degraded result; outcome persistence records the degradation without throwing in the primary agent turn.

- [ ] Write failing tests with a fake transport that fails twice then succeeds, and one that always times out; assert attempt count, bounded delay callback calls, and final degraded envelope.
- [ ] Run the focused tests and confirm the existing one-shot client does not satisfy them.
- [ ] Implement injectable sleep/clock dependencies, retry classification, exponential delay, timeout handling, and typed degraded envelopes.
- [ ] Make provider code surface the degraded recall message and log sanitized observability metadata.
- [ ] Re-run all Hermes tests in the declared dependency environment.
- [ ] Commit the story-owned files with `feat: add Hermes degraded retry contract`.

### Task 7: P-1.5 — Release gate and evidence receipt

**Files:**
- Modify: `docs/PUBLIC-RELEASE-PLAN.md`, `README.md`, `.github/workflows/ci.yml`, `_bmad/bmm/stories/p-1-5-public-release-gate.md`
- Create: `docs/release-evidence/2026-08-24-plugin-catalog-release.md`

**Interfaces:**
- CI has independent `catalog`, `evals`, `runtime-sync`, `skill-dependencies`, and `hermes` jobs.
- Release evidence lists exact command, commit SHA, exit status, and reviewer verdict; it never contains secret values.

- [ ] Write a failing CI-configuration test that requires all five named jobs and the dependency-install step.
- [ ] Run the test and confirm the existing workflow lacks the jobs.
- [ ] Add the jobs, pinned dependency installation, and branch/PR execution.
- [ ] Execute all local release commands from a clean dependency environment; attach fresh outputs to the evidence receipt.
- [ ] Have Pike review interface boundaries and Fowler review maintainability/acceptance criteria.
- [ ] Update P-1.5 only after every dependency story has independently verified evidence.
- [ ] Commit the release-gate artifacts with `chore: add plugin catalog release evidence`.

## Self-Review

- P-1.2, P-1.3, P-1.4 each have independent scripts, behavior tests, CI coverage, and feed P-1.5.
- P-2.1 establishes contracts used by P-2.2 and P-2.3; tenant and retry work are not combined.
- The Hermes dependency blocker is handled through a declared test environment, not skipped tests or host-local assumptions.
- No task relies on untyped tenant input, hidden OpenCode assumptions, or raw source-text assertions.
