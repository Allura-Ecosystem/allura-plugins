# Adaptive workflow upgrade — 2026-10-13

This release is prepared locally for review. Source commits must be published
before a remote catalog build can fetch the new pins. No runtime installation,
external publishing, deployment, or memory promotion is performed by this release.

## Changes

- RAM 0.5.0 removes Scout-text-length escalation, preserves the selected owner on
  the first iteration, inherits the host model and prevents definition loading
  from being reported as successful execution.
- Durham 0.4.0 selects quick/standard/sensitive routes and permits independent
  preparation after approved inputs. Strategy, naming dependencies, independent
  review and human promotion/shipping gates remain.
- Allura Cowork 0.3.0 uses one accountable owner, fresh scoped context and selective
  handoffs. Modern models are selected by host configuration and evaluated capability.
- Bumblebee 0.1.1 ships real entry skills for read-only evidence review; no scanner
  engine or upstream dependency was changed.
- Mortgate Cowork 0.2.1 reuses same-case cited evidence while retaining every
  human review and prohibited-action boundary. Its Microsoft export has 23 files.
- Hermes Brain 0.2.0 receives context-sharing guidance only. Provider code and
  authentication behavior are unchanged.
- The internal Allura README pack 0.1.1 has completed manifest metadata and bounded
  writer guidance; it remains outside public marketplaces.

## Source and package authority

`source-locks.json` records exact standalone revisions. Generated RAM, Durham,
Mortgate and Bumblebee packages must be regenerated rather than hand-edited.
`scripts/sync_catalog_metadata.py` derives catalog versions and discovery from
the generated manifests; it does not touch installed runtime settings.

Native Microsoft and Hermes packages are not portable Claude/Codex plugins.
Codex manifest validation rejects unsupported Claude fields. Role guidance is
distinct from native subagent registration. Use plugin-qualified skill/command
names when RAM and Durham share names such as `auto`, `party` and `scout`.

For review before the source branches are published, run from the catalog root:

```bash
python3 scripts/verify_source_exports.py --check \
  --source team-ram=../allura-team-ram \
  --source team-durham=../team-durham \
  --source mortagate-cowork=../mortagate \
  --source bumblebee=../bumblebee
python3 scripts/sync_catalog_metadata.py --check
python3 scripts/validate_manifests.py
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests -q
bash scripts/commands-audit.sh
```

Local source overrides require the matching origin and locked commit. They clone
committed objects into a clean temporary checkout; dirty source files never enter
the package. Allowlists, provenance, version parity, file inventories and secret
checks still apply. CI uses remote locked revisions with no overrides.

## Evidence limits and rollout

Static prompt/manifest checks and routing regressions establish package behavior;
they do not demonstrate model quality or a measured speedup. Model evaluation
and performance scripts return `not-run` without actual model runs/measurements.
Compare representative tasks with identical acceptance criteria before claiming
latency or cost gains. Keep review independence and protected-operation authority.

RAM's direct Anthropic adapter is text-only. Tool-dependent implementation/auto
tasks require a capable host runtime; this release fails those unsupported calls
honestly instead of claiming that generated text changed a workspace. Adaptive
context reuse/review rules are host instructions, not a newly deployed scheduler.

Mortgate's independent blind behavioral evaluation and tenant/toolkit gates remain
pending. Source/package checks do not constitute production approval. See its
source evidence file `my-project/_bmad-output/test/cowork-workflow-review-2026-10-13.md`.
Its pre-existing fixture arithmetic discrepancy also needs separate resolution.

Brain tools were unavailable during this upgrade. No hydration or outcome-write
receipt is claimed. Local branches and test evidence preserve the reviewable work.

Publish source branches and resolve required domain gates before publishing the
catalog pins. Install from the validated release only after publication or an
explicitly selected local development marketplace. Start a new runtime session
after installation so it can load the updated skills and model policy.

## Validation receipt

- RAM: 111 tests passed; typecheck, source export and adapter synchronization passed.
- Durham: 18 deterministic routing/dependency cases plus repository/export validation passed.
- Catalog: 53 regression tests passed; all four source pins reproduce without drift.
- Native Codex validators: Cowork, Durham, RAM and Bumblebee passed.
- Model policy audit: 71 agent surfaces checked, zero inheritance drift.
- Command audit: zero orphan commands; 13 shared RAM/Durham names documented above.
- Secret scan and whitespace checks passed.

RAM's optional legacy `scripts/lint-agents.sh` has a pre-existing broken sed
expression; the main lint and canonical synchronization checks passed.
