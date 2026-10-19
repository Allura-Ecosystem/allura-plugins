# Workflow evaluation — 0.1.1

> AI-assisted documentation. Evaluated by source review on 2026-10-13; these are
> contract checks and an in-session walkthrough, not live scanner/runtime tests.

| Scenario | Review result |
|---|---|
| Existing fresh report, matching tenant/workspace/source/profile | Skill permits direct read-only answer without repeated intake. |
| Same report but different tenant or changed source revision | Scope mismatch requires refreshed evidence; no cross-scope reuse. |
| Old report or missing completion time | Stale/unknown, never a clean security result. |
| Partial/timeout batch | Held evidence; no replacement of trusted inventory. |
| Deep scan alongside routine inventory | Kept separate. |
| User requests promotion or remediation | Outside this skill; governed workflow required, no mutation executed. |
| No connector available | Supplied-artifact review only; no claim of live endpoint verification. |
| New host model | User-configured model retained; security authority unchanged. |

Validation: plugin manifest validation, JSON parsing, matching 0.1.1 distribution
versions, non-empty declared skill/command paths, and whitespace checks. Scanner,
network, runtime throughput, and provider-specific behavior were not exercised.
