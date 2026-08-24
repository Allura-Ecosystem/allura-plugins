# Team RAM

A Team RAM agent platform for Allura-governed development in Claude Code and
Codex CLI. Brooks leads; Scout recon, Woz implements, Fowler reviews.

## What It Is

Team RAM packages the Brooks-led Team RAM agent surface: agents for
architecture, scouting, implementation, and review; commands for session
lifecycle, goal definition, context management, and validation; and skills
for memory, code review, task management, multi-source research, secret
management, and party-mode multi-agent dispatch.

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

35 commands covering: `start-session`, `end-session`, `scout`, `architect`,
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

## Package Contract

### Runtime manifests

This portable package is published at `team-ram-coding/` through the root
Claude marketplace and owns `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json`. Its public installation path is
`team-ram-coding@allura-ecosystem`. It is the catalog-distributed Team RAM
package; the standalone `allura-team-ram` harness is a separate product.

### Validation

Run the package review gates documented in this package's skills, then run
`python3 scripts/validate_manifests.py` from the catalog root to verify public
manifest paths and catalog contract metadata.

### Dependencies and degraded behavior

Allura Brain is expected for memory-dependent workflows. Docker is optional for
the `mcp-docker` and `varlock` skills; unavailable dependencies cause the
affected skills to report a visible degraded state rather than claim execution.