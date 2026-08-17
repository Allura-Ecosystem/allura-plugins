# Risks and Decisions

## Decisions

### AD-001: Dedicated Organization Catalog

**Date:** 2026-06-11
**Decision:** Use `Allura-Ecosystem/allura-plugins` as the catalog authority.
**Reason:** Plugin release cadence and validation should not be coupled to the
Allura Memory product repository.

### AD-002: Private First

**Date:** 2026-06-11
**Decision:** Keep the repository private during inventory and validation.
**Reason:** Existing package copies have not completed provenance, secret, and
path scans.

### AD-003: Capability Parity

**Date:** 2026-06-11
**Decision:** Align capabilities, not implementation mechanics.
**Reason:** Claude and Codex have different plugin, hook, and MCP surfaces.

### AD-004: Hybrid Model Routing — Config as Enforcement Point

**Date:** 2026-08-17
**Status:** Decided
**Decision:** Route Team RAM and Team Durham agents to five model contracts via harness configuration (`opencode.json` and OpenWork `runtime-opencode-config.json`), not via a separate registry or front-matter declarations. The harness config is the runtime enforcement point.

**Model contracts:**

| Contract | Model | Scope |
|---|---|---|
| Architecture / final judgment | Codex `gpt-5.6-terra` (fallback: `glm-5.2:cloud` until OPENAI_API_KEY is set) | Architecture, security, data decisions, final review, release gates |
| Routine coding | Ollama Cloud `kimi-k2.7-code:cloud` | Contained implementation, test creation, routine fixes |
| General specialist work | Ollama Cloud `glm-5.2:cloud` | Recon, analysis, research, copy, evidence collection |
| Vision / visual QA | Ollama Cloud `qwen3.5:397b-cloud` | Visual direction, brand work, visual QA |
| Scout / low-cost first pass | Ollama Cloud `nemotron-3-super:cloud` | Scout recon, mechanical drafting, classification |
| Retrieval embeddings | Local `qwen3-embedding:8b` | Allura retrieval only |

**Rationale:** A separate `contracts.json` registry with `model_contract` front-matter fields duplicates what the harness config already does. The config maps agents to models — that is the enforcement point. Pike review identified that the registry approach adds a second system with no consumer. The simpler path is to put the policy directly in the config and document it here.

**Alternatives Considered:**
1. Separate `contracts.json` + `model_contract` front matter — rejected; no runtime adapter consumes the field; adds complexity without enforcement.
2. Build a custom router/adapter — deferred; the harness configs already provide model selection; a custom adapter is accidental complexity until the configs are proven insufficient.
3. Single-model for all agents — rejected; different task classes have different cost/quality tradeoffs.

**Consequences:**
- Architecture agents temporarily use `glm-5.2:cloud` as fallback until `OPENAI_API_KEY` is configured for Codex Terra.
- GPT-5.6 Luna is reserved for future low-cost first-pass work but not yet assigned to any agent.
- Escalation from routine to architecture is manual until a runtime adapter is built.
- Allura records route evidence but does not alter routing policy.

**Owner:** Brooks
**References:** `team-durham/docs/superpowers/specs/2026-08-16-hybrid-model-routing-design.md`, OpenCode config `~/.config/opencode/opencode.json`, OpenWork config `~/.config/openwork/runtime-opencode-config.json`

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| RK-01 | A newer timestamp hides older behavior. | Compare upstream Git revisions, tests, manifests, and hashes. |
| RK-02 | Claude and Codex hook schemas diverge. | Validate separately and maintain runtime-specific hook files. |
| RK-03 | A package contains secrets or absolute paths. | Block release on secret and path scans. |
| RK-04 | Global team plugins bypass project routing. | Separate installation availability from project activation policy. |
| RK-05 | Config text appears correct while runtime load fails. | Require native list output and restart verification. |
