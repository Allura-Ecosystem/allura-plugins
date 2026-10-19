---
name: bumblebee-review
description: Review supplied Bumblebee scan summaries, inventory freshness, held batches, and vulnerability exposure evidence without changing endpoint or server state.
---

# Bumblebee evidence review

Use this skill for read-only review of an existing scan or exposure report.

## Scope and authority

- Use the user's configured model; this skill requires evidence interpretation, not a fixed provider or model generation.
- Review supplied evidence or use an available authorized read-only connector. This plugin does not bundle a scanner binary or a live connector.
- Do not install packages, run a new scan, change source enrollment, mint credentials, ingest records, promote a batch, or remediate an endpoint as part of this review. Explain the required governed workflow when asked for those operations.
- Never relax authentication, tenant/workspace binding, scanner pinning, redaction, HTTPS, validation, or fail-closed policy. Do not expose credentials or unredacted sensitive scan payloads.

## Workflow

1. Identify the question and the tenant, workspace, source revision, endpoint population, profile, and evidence timestamp available to answer it. Ask only for missing inputs essential to that question; an unknown scope supports only a qualified description of the supplied artifact.
2. Reuse an existing context packet only when those identifiers, the source evidence, and permissions still match. Recheck the server-provided freshness and state; a previous review is not a new scan. Changed scope, source revision, profile, permissions, new evidence, or stale state requires refreshed evidence. Never reuse credentials as context.
3. Answer a clear, authorized read-only request directly with one owner. Load only the relevant references below. Do not add an intake menu, repeated confirmation, or a specialist handoff without a concrete unresolved question.
4. Distinguish fresh complete inventory, known-empty inventory, stale data, held partial evidence, and endpoint-asserted findings. Missing or stale evidence is never a clean security result. Never combine deep campaign scans with routine inventory.
5. Report the finding, source identifiers/timestamps, server-reported status, and uncertainty. Describe a finding as trusted exposure only when the server's authority evidence establishes package/version/catalog matching. Model confidence cannot promote or verify evidence.

## Targeted references

- State and promotion: `../../docs/state-model.md`
- Security and privacy: `../../docs/security.md`
- Scanner pin: `../../docs/upstream-pin.md`
- Transport authority: `../../docs/transport.md`

## Completion

Return a concise evidence-backed answer and any specific missing evidence. Distinguish artifact review from live endpoint verification. A faster model or reused context never expands this skill's authority.
