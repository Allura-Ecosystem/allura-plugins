# Roadmap

## Shipped (v0.2.0)

- 3-plugin marketplace: `allura-cowork`, `team-durham`, `team-ram-coding`
- Claude Code and Codex CLI manifests for all 3 plugins
- CI validation: marketplace sources resolve, manifests parse, referenced files exist, no hardcoded paths
- MIT license

## Next

- Expand eval fixture coverage beyond the current 5 agents
- OpenCode three-way sync (currently OpenCode tree is a separate surface)
- Per-skill dependency detection (graceful no-op when a service is absent)

## Release Gate

See `docs/PUBLIC-RELEASE-PLAN.md` for the full release checklist.