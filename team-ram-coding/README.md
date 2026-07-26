# Team Ram Coding

A Team RAM coding plugin for Allura-governed Brooks, Jobs, Scout, and Woz
workflows in Claude Code and Codex CLI.

## What It Is

Team Ram Coding packages the Brooks-led Team RAM coding surface: agents for
architecture, scouting, implementation, and review; commands for session
lifecycle, goal definition, context management, and validation; and skills
for memory, code review, task management, and multi-source research.

The plugin enforces Allura governance defaults: memory search before action,
runtime honesty, validation evidence, and outcome logging.

## Agents

- **Brooks** — system architect and technical design leader
- **Jobs** — product and UX direction
- **Scout** — recon and discovery
- **Woz** — primary builder and implementation
- **Knuth** — data architect
- **Pike** — interface review
- **Fowler** — refactor gate
- **Bellard** — diagnostics and performance
- **Carmack** — performance optimization
- **Hightower** — infrastructure and DevOps
- **Bahari** — general-purpose fallback

## Commands

34 commands covering: `start-session`, `end-session`, `scout`, `architect`,
`ralph`, `debug`, `test`, `commit`, `clean`, `optimize`, `validate-repo`,
`query`, `task`, `goal`, `context`, `party`, `orchestrate`, and more.

## Requirements

- **Claude Code** or **Codex CLI** with plugin support.
- **Allura Brain** (expected) — most skills assume the memory MCP is
  reachable at the configured endpoint. Without it, memory-dependent
  commands will report the missing connection.
- **Docker** (optional) — the `mcp-docker` and `varlock` skills use the
  Docker MCP toolkit. Without Docker, those skills no-op gracefully.
- **Allura Memory repository** — the `allura-memory-skill` documents how to
  configure the memory MCP server. Set `ALLURA_MEMORY_ROOT` to point at your
  local checkout.

## Install

Add the Allura marketplace, then install:

```
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install team-ram-coding@allura-ecosystem
```

## License

MIT — see [LICENSE](../LICENSE).