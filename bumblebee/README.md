# Bumblebee

Review software supply-chain evidence and explain what it does—and does not—establish about an endpoint.

The installable plugin provides one read-only review skill and command. Give it an existing scan summary, inventory report, or exposure finding; it helps distinguish current inventory, stale data, incomplete evidence, and server-verified exposure. It uses the host's configured model and available tools.

The scanner and Allura server integration are separate components. Installing this package does not install a scanner binary, start a scan, connect to a server, or enable ingestion.

> **AI-Assisted Documentation** — this guide was prepared with AI assistance. Source code and current runtime evidence remain authoritative.

## Install and use

In Claude Code:

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install bumblebee@allura-ecosystem
/bumblebee:bumblebee-review
```

For Codex, use the [catalog installation guide](https://github.com/Allura-Ecosystem/allura-plugins#codex) and load the `bumblebee-review` skill through the available skill interface.

Supply the evidence and a question, for example:

> Review this scan summary. Identify its scope and timestamp, explain any held or stale state, and say which vulnerability claims still need server evidence.

The [review skill](skills/bumblebee-review/SKILL.md) returns findings, source references, reported status, uncertainty, and missing evidence. It can also use an existing authorized read-only connector. It does not install packages, mint credentials, ingest records, promote batches, or remediate endpoints.

## What a review can establish

| Evidence state | How the review treats it |
|---|---|
| Fresh, complete inventory | Describe the server-reported scope and freshness |
| Known-empty inventory | Report the explicit empty result with its scope |
| Stale data | State its age and the need for refreshed evidence |
| Held or partial scan | Describe available findings without replacing current inventory |
| Endpoint-asserted finding | Keep the claim qualified until server authority evidence supports it |
| Server-verified exposure | Require package, version, and advisory-catalog matching evidence |

Missing evidence is not a clean security result. A previous review is not a new scan. Reuse context only while scope, source revision, profile, evidence, and permissions still match. See [workflow evaluation](docs/workflow-evaluation.md) for the `0.1.1` review contract.

## How it works

```text
Supplied scan or exposure evidence
  → Review scope, source, freshness, and reported state
  → Distinguish verified findings from incomplete claims
  → Return cited findings and missing evidence
```

This flow describes the installed skill. The optional server architecture below has additional deployment and authorization requirements.

## Server integration reference

The Allura implementation lives in [`Allura_Memory`](https://github.com/Allura-Ecosystem/Allura_Memory), not this repository. It wraps the pinned upstream [`perplexityai/bumblebee`](https://github.com/perplexityai/bumblebee) scanner with source enrollment, scan leases, ingestion checks, stored evidence, and exposure matching. Current deployment and endpoint access must be verified separately.

Paths below are relative to `src/lib/bumblebee/` in Allura Memory:

| Stage | Source | Responsibility |
|---|---|---|
| Source enrollment | `source-authority.ts` | Bind scanner pin, scope, classification, and redaction policy |
| Lease issuance | `lease-authority.ts` | Separate runner authority from short-lived ingestion credentials |
| Secure ingestion | `ingest-pipeline.ts` | Check transport, authentication, bounded input, replay, and conflicts |
| Record validation | `batch-conformance.ts` | Validate NDJSON, identifiers, counts, and sanitized records |
| Snapshot decision | `promotion-engine.ts` | Decide whether a batch becomes inventory or remains held evidence |
| Exposure matching | `finding-authority.ts` | Match reported findings to package, version, and advisory evidence |

“Promotion” in this server reference means a scan snapshot becoming inventory. It does not grant an agent permission to promote Allura semantic memory or to invoke this server operation through the review skill.

### Code location

| Surface | Path in Allura Memory |
|---|---|
| Core library | `src/lib/bumblebee/` |
| API routes | `src/app/api/plugins/bumblebee/{runs,ingest}/` |
| Curator UI | `src/components/bumblebee/surfaces.tsx` |
| Tests | `src/lib/bumblebee/__tests__/` |
| Planning records | `_bmad/bmm/planning/epic-26-*.md` |

Additional implementation modules cover credential bootstrap and tenant transactions (`lease-repository.ts`), atomic receipts and records (`batch-store.ts`), inventory freshness (`staleness.ts`), and exposure persistence (`exposure-store.ts`). See [architecture and data flow](docs/architecture.md).

### Upstream scanner pin

| Field | Value |
|---|---|
| Repository | `perplexityai/bumblebee` |
| Tag | `v0.1.2` |
| Commit | `cc57710eeaf685e7b89924a36c8583cad0a378fe` |
| Tree | `985f57cf1749c15561c886c4476f10950ffa9cae` |
| Schema version | `0.1.0` |
| Upstream license | Apache-2.0 |

The server's `upstream-contract.ts` declares this pin. The plugin package itself is MIT licensed; see [LICENSE](LICENSE).

## Validation and release limits

The repository packages the review instructions, command, manifests, and documentation. Review its [workflow evaluation](docs/workflow-evaluation.md) and the catalog's [validation guide](https://github.com/Allura-Ecosystem/allura-plugins#validation) when releasing changes.

Current server readiness, runtime installation, and endpoint state require evidence from the relevant deployment. The server feature flag is default-off and requires exact `BUMBLEBEE_MODULE_ENABLED=true`; installing the review plugin does not set it.

## Further reading

- [Framework mapping](docs/framework-mapping.md)
- [Architecture and data flow](docs/architecture.md)
- [Transport and authentication](docs/transport.md)
- [Upstream pin and schema](docs/upstream-pin.md)
- [State and promotion](docs/state-model.md)
- [Security and privacy](docs/security.md)
