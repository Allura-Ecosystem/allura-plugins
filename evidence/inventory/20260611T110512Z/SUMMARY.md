# Pre-Migration Inventory Summary

**Generated:** 2026-06-11 11:05:12 UTC  
**Runtime configuration changed:** No

## Recovery Evidence

- Timestamped Claude and Codex configuration backups exist locally under the
  gitignored `evidence/backups/20260611T110512Z/`.
- Existing marketplace and local plugin trees were archived.
- Configuration and plugin-tree hashes are recorded in `inventory.json`.

## Runtime Findings

- Claude reports 12 installed plugins overall.
- Claude has `allura-governance@allura-local` version `0.1.3` installed but
  disabled.
- Claude's available Allura marketplace still advertises legacy names including
  `allura-memory-cowork`, `allura-scout`, and `team-ram`.
- Codex reports zero installed plugins.
- Codex exposes home-local Allura candidates, but each is reported
  `installed: false` and `enabled: false`.

## Candidate Findings

- 116 plugin or marketplace manifest paths were found.
- 28 Allura, Team RAM, or Team Durham package copies were identified.
- Multiple packages share names and versions but have different content hashes.
- `allura-governance` has versions `0.1.0` through `0.1.3` across caches and
  marketplace copies.
- `team-durham` is split between Claude-only and Codex-only package copies.
- `team-ram-coding` has a dual-runtime candidate at
  version `0.1.0+codex.20260530050504`.

## Next Gate

Select package candidates from upstream repository truth and validation
evidence. Filesystem timestamp or version text alone is insufficient.
