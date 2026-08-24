# Epic P-1 — Plugin Catalog Release

**Status:** In Progress
**Owner:** Brooks (architecture) + Woz (implementation)
**Tenant:** allura-system
**Repo:** `plugins/allura-plugins/`

## Goal

Ship the Allura plugin catalog as a validated, publicly releasable set of Claude/Codex packages plus a first-class Hermes-native Allura Brain connector, with CI-verified manifests, expanded eval coverage, and explicit runtime boundaries.

## Product Boundary

`allura-plugins` is the canonical source and governance repository for the Allura plugin layer. It owns the plugin catalog, model governance, Hermes-native connector packaging, and release evidence. Plugins add skills, commands, and operating roles; they do not replace Allura Brain or bypass its memory governance.

## Current State

- Claude marketplace: `allura-cowork`, `team-durham`, and `team-ram-coding`.
- Hermes-native connector: `plugins/hermes-allura-brain/plugin.yaml` (`allura-brain` v0.2.0).
- P-1.1 implementation is underway: CI delegates to `scripts/validate_manifests.py`, which validates marketplace and runtime manifests.

## Story Map

| Story | Outcome | Dependency | Ship condition |
|---|---|---|---|
| P-1.1 | Marketplace CI hardening | — | Catalog manifests and Hermes native manifest validate; paths resolve; no hardcoded paths |
| P-1.2 | Eval fixture expansion | P-1.1 | Eval coverage beyond 5 agents with pass/fail evidence |
| P-1.3 | OpenCode three-way sync | P-1.1 | Claude/Codex/OpenCode surfaces reconciled and drift detected |
| P-1.4 | Per-skill dependency detection | P-1.1 | Skills visibly no-op when a dependency is absent |
| P-1.5 | Public release gate | P-1.1, P-1.2, P-1.3, P-1.4 | Full release checklist passes |

## Dependencies

- Allura Memory canonical docs and governance
- Allura Brain MCP server for runtime validation

## Rollback

Plugins are additive. Disabling a catalog package or Hermes provider does not affect the engine or other plugins.
