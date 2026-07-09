# Team Durham OpenCode Plugin

`team-durham.ts` registers the project-local Team Durham plugin metadata for OpenCode.

Callable project agents live in:

```text
.opencode/agents/
```

The plugin exports:

- `TEAM_DURHAM_AGENTS` — agent names, personas, source files, canonical files, user IDs, and memory queries.
- `TEAM_DURHAM_MEMORY` — shared Allura Brain group and tool aliases.
- `TeamDurham` — minimal OpenCode plugin entry point.

This layer complements, but does not replace:

- `.opencode/agent/*/AGENTS.md` legacy wrappers
- `.claude/agents/*.md` canonical definitions
- `_bmad/custom/*.toml` BMAD persona overrides

