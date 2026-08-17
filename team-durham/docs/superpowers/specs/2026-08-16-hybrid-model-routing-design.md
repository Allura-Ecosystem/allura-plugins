# Hybrid Model Routing Design

**Status:** Decided (AD-004); implementation in progress — config-as-enforcement
**Date:** 2026-08-17 (updated from 2026-08-16)
**Scope:** Team RAM Coding and Team Durham model-routing across OpenCode and OpenWork harnesses

## Purpose

Replace the present patchwork of model assignments with five stable model
contracts. The system uses the available Codex/OpenAI subscription for
high-consequence engineering judgment and Ollama Cloud subscriptions for
routine specialist throughput. Allura supplies evidence and audit history;
it does not autonomously change the routing policy.

## Model Contracts

| Contract | Default model | Work assigned |
| --- | --- | --- |
| Architecture and final judgment | Codex `gpt-5.6-terra` (fallback: `glm-5.2:cloud` until OPENAI_API_KEY is set) | Architecture, security and data decisions, complex debugging, final review, release gates |
| Routine coding | Ollama Cloud `kimi-k2.7-code:cloud` | Contained implementation, test creation, routine fixes |
| General specialist work | Ollama Cloud `glm-5.2:cloud` | Recon, analysis, research synthesis, copy, and evidence collection |
| Vision and visual QA | Ollama Cloud `qwen3.5:397b-cloud` | Visual direction, image-informed brand work, and visual QA |
| Scout / low-cost first pass | Ollama Cloud `nemotron-3-super:cloud` | Scout recon, mechanical drafting, classification |
| Retrieval embeddings | Local `qwen3-embedding:8b` | Allura embedding and retrieval only; never agent reasoning |

**Reserved for future:** GPT-5.6 Luna for low-cost first-pass lane (not yet assigned to any agent).

## Routing Rules

1. A task is assigned by its declared class, not by a model's self-reported
   confidence.
2. Architecture, cross-interface changes, security/data decisions, final
   review, and release decisions route directly to Codex.
3. Routine implementation begins on the routine-coding contract.
4. A task escalates to Codex when its provider is unavailable, it produces
   malformed structured/tool output, it fails a defined quality gate, or a
   second implementation attempt fails validation.
5. Vision work uses the vision contract; text-only work must not use it merely
   because it is larger.
6. Current secondary Ollama models remain installed and available for manual
   incident response, but are not automatic defaults.

## Allura Evidence Contract

Every completed routed task records an append-only episodic event containing:

- task class and responsible agent;
- selected provider and model;
- fallback or escalation reason, if any;
- latency and available token/cost fields;
- validation evidence: tests, schema validation, review result, or human
  acceptance.

Allura may recommend a revised route after sufficient evidence exists. Route
changes remain a governed architectural decision requiring explicit approval.
Raw event traces are not canonical knowledge and are promoted only after
reusable, validated evidence exists.

## Failure Handling

- Provider timeout/rate limit/unavailability: retry only where the runtime
  guarantees idempotence, then use the declared fallback.
- Invalid structured response: retry once on the fallback and retain both
  receipts.
- Failed test or review: return to the responsible implementation contract;
  escalate after the second failed attempt.
- Sensitive input: preserve the project's classification policy; a model
  routing rule never overrides data-handling restrictions.

## Enforcement Approach

Per AD-004 and Pike review, the harness configuration files are the enforcement point — not a separate registry. Agent model assignments live directly in:
- OpenCode: `~/.config/opencode/opencode.json` → `agent.*.model`
- OpenWork: `~/.config/openwork/runtime-opencode-config.json` → `agent.*.model`

A separate `contracts.json` + `model_contract` front-matter system was rejected as duplicative complexity with no runtime consumer.

## Configuration Impact

Implementation updates the harness configs directly:
- OpenCode: corrected 27 model name mismatches (`:0813`/`:0731` → `:cloud`, bare names → `:cloud` suffix) and applied the approved roster.
- OpenWork: added provider, model, and small_model sections that were entirely absent.
- Both configs use `ollama/` prefix with `:cloud` suffix for all cloud models.

## Validation Criteria

1. Each agent resolves to one of the five contracts.
2. All high-consequence task classes route directly to Codex.
3. Each fallback path is deterministic and testable without a live provider.
4. A completed task writes an evidence trace with route and validation result.
5. Existing skill and agent references contain no stale default model route.
