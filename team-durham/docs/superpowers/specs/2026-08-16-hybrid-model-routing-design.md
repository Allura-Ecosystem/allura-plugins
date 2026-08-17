# Hybrid Model Routing Design

**Status:** Approved design; implementation not started
**Date:** 2026-08-16
**Scope:** Team RAM Coding and Team Durham model-routing declarations

## Purpose

Replace the present patchwork of model assignments with five stable model
contracts. The system uses the available Codex/OpenAI subscription for
high-consequence engineering judgment and Ollama Cloud subscriptions for
routine specialist throughput. Allura supplies evidence and audit history;
it does not autonomously change the routing policy.

## Model Contracts

| Contract | Default model | Work assigned |
| --- | --- | --- |
| Architecture and final judgment | Codex `gpt-5.6-terra` | Architecture, security and data decisions, complex debugging, final review, release gates |
| Routine coding | Ollama Cloud `kimi-k2.7-code:cloud` | Contained implementation, test creation, routine fixes |
| General specialist work | Ollama Cloud `glm-5.2:cloud` | Recon, analysis, research synthesis, copy, and evidence collection |
| Vision and visual QA | Ollama Cloud `qwen3.5:397b-cloud` | Visual direction, image-informed brand work, and visual QA |
| Retrieval embeddings | Local `qwen3-embedding:8b` | Allura embedding and retrieval only; never agent reasoning |

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

## Configuration Impact

Implementation will update the Team RAM Coding agent declarations and Team
Durham routing declarations, add a provider-neutral routing policy, and add
the Allura event schema/emitters needed for the evidence contract. It will not
delete installed Ollama models or mutate historic Allura records.

## Validation Criteria

1. Each agent resolves to one of the five contracts.
2. All high-consequence task classes route directly to Codex.
3. Each fallback path is deterministic and testable without a live provider.
4. A completed task writes an evidence trace with route and validation result.
5. Existing skill and agent references contain no stale default model route.
