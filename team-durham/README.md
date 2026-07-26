# Team Durham

A multi-agent brand production team for Claude Code and Codex CLI.

Team Durham packages a complete design-team harness for brand production:
strategy, naming, visual direction, brand kit assembly, QA, memory, and
delivery. Twelve canonical agents, ~70 skills, 21 commands, governance
rules, and persona research.

## Core Agents

| Agent | Persona | Canonical Role |
|-------|---------|----------------|
| Kotler | Philip Kotler | Brand Orchestrator + STP gate |
| Aaker | Jennifer Aaker | Brand Strategy + personality |
| Ogilvy | David Ogilvy | Naming, copy, voice |
| Glaser | Milton Glaser | Visual direction + logo |
| Rand | Paul Rand | Brand kit + design system |
| Munari | Bruno Munari | QA, consistency, accessibility |
| Tufte | Edward Tufte | Evidence, data, competitive intelligence |
| Scout | Utility | Fast read-only recon |
| Reality Checker | Allura Ops | Evidence-based readiness |
| Evidence Collector | Allura Ops | Screenshot/artifact proof |
| Workflow Architect | Allura Ops | Handoffs and state machines |
| Agentic Trust Architect | Allura Ops | Permissions, audit, memory trust |

## Operating Rules

- STP before pixels.
- Search before write.
- Brand truth is canonical once locked.
- QA is read-only: Munari flags, producers fix.
- Project-specific governance applies only to that project.
- Persona research grounds voice, but governance wins.

## Requirements

- **Claude Code** or **Codex CLI** with plugin support.
- **Allura Brain** (expected) — most skills assume the memory MCP is
  reachable. Without it, memory-dependent commands report the missing
  connection rather than fail silently.
- **Docker** (optional) — the `mcp-docker`, `mcp-docker-memory`,
  `docker-presentation-server`, and `mcp-validation-gate` skills use the
  Docker MCP toolkit.
- **fal.ai** (optional) — `fal-ideogram-executor`, `falai-runner`, and
  `fal-ai-image-prompt-engineering` require `FAL_KEY`.
- **Figma** (optional) — `figma-*` skills require `FIGMA_TOKEN`.
- **Notion** (optional) — `notion-*` skills require `NOTION_TOKEN`.
- **LibreOffice** (optional) — `mcp-libre` requires LibreOffice and the
  `fastmcp` CLI. Set `MCP_LIBRE_ROOT` to the server install path.

## Install

Add the Allura marketplace, then install:

```
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install team-durham@allura-ecosystem
```

## License

MIT — see [LICENSE](../LICENSE).