# Source-first catalog export sync

`allura-plugins` is a generated distribution catalog. Team/product content is owned by standalone repositories and enters this catalog only through the export contract and full Git SHA pinned in [`source-locks.json`](source-locks.json).

```text
standalone canonical repository @ locked SHA
        ↓ canonical exporter/allowlist contract
catalog generated destination
        ↓ marketplace/runtime installation
runtime-local copy (never an upstream source)
```

## Commands

```bash
# Regenerate all three exports in temporary directories and fail on any drift
./harness-sync.sh --check

# Replace every generated destination from its pinned standalone source
./harness-sync.sh --sync

# Compatibility selectors retained from the prior command surface
./harness-sync.sh --check --team ram
./harness-sync.sh --sync --team durham
./harness-sync.sh --check --project team-ram-coding
./harness-sync.sh --check --team mortagate
```

`--check` clones each public repository, proves the locked commit exists in that remote clone, checks out the exact full SHA, runs the canonical exporter (or Mortagate's exact contract allowlist), validates provenance and versions, scans for secret-like material, and compares every exported entry by path, kind, size, and SHA-256. Missing, changed, or unexpected files fail the command.

`--sync` performs the same generation and validation, then replaces each generated destination by whole-directory replacement and reads it back for an exact inventory comparison.

The retired behavior that copied a catalog directory into arbitrary project overlays no longer exists. Catalog content is never canonical and no command copies it upstream or into product repositories.

## Locked packages and aliases

| Standalone authority | Generated destination | Runtime | Compatibility identity |
|---|---|---|---|
| [Team RAM](https://github.com/Allura-Ecosystem/allura-team-ram) | `team-ram-coding/` | Claude, Codex, OpenCode | Marketplace install name/path remains `team-ram-coding`; generated source manifests remain `team-ram-harness` |
| [Team Durham](https://github.com/Allura-Ecosystem/team-durham) | `team-durham/` | Claude, Codex, OpenCode | Marketplace install name/path remains `team-durham` |
| [Mortagate](https://github.com/Allura-Ecosystem/mortagate) | `packages/mortagate-cowork/` | Microsoft Cowork | Runtime-neutral catalog entry only; deliberately absent from Claude marketplace |

Do not rename generated Team RAM manifests to the marketplace alias. The root marketplace resolves `team-ram-coding` to the generated directory; CI verifies that alias and then verifies the source-owned `team-ram-harness` manifest and all of its install paths.

## Manual edits are forbidden

Generated package files are not authoritative. Make content changes in the owning standalone repository, update its export contract and release version there, push it, review the export, then update the full SHA/version fields in `source-locks.json` and run `./harness-sync.sh --sync`.

Team RAM's exported `.mcp.json` files are accepted only when they contain the exact localhost Allura Brain endpoint and no embedded `env` credentials. Mortagate is built from the contract's exact 19-file allowlist; repository-root `.mcp.json`, local configuration, build output, and all non-allowlisted files cannot enter the package.
