# Story P-1.1 — Marketplace CI Hardening

**Status:** In Progress
**Owner:** Woz + Pike
**Depends on:** —
**Blocks:** P-1.2, P-1.3, P-1.4, P-1.5

## Outcome

All catalog manifests, including the Hermes-native provider manifest, validate; referenced paths resolve; and no hardcoded paths remain—verified by CI on every push.

## Acceptance Criteria

- [ ] All three Claude/Codex catalog package manifests parse without errors.
- [ ] The Hermes-native `plugin.yaml` has a name, version, description, and the canonical `allura-brain` identity.
- [ ] Every referenced file path in catalog package manifests resolves to a real file.
- [ ] No hardcoded absolute paths exist in shipped catalog package source.
- [ ] CI runs validation on every push and blocks on failure.
- [ ] Marketplace sources resolve correctly in Claude Code and Codex CLI.

## Evidence

- CI manifest validation output.
- Path resolution test results.
- Hardcoded-path sweep returns zero results.
- Hermes manifest validation output.

## Rollback

Revert CI configuration. Plugins remain functional; validation is not enforced.
