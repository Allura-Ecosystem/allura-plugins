# Team Durham Codex Plugin

Team Durham is a multi-agent brand production team for Codex.

This plugin packages the Brand Maker harness into a reusable local plugin:

- Canonical agent definitions in `agents/`
- Shared production skills in `skills/`
- Command runbooks in `commands/`
- Governance and routing rules in `rules/` and `governance/`
- Persona research and Codex aliases in `source/codex/`
- OpenCode adapter references in `source/opencode/`
- BMAD Builder persona overrides in `source/bmad/`

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

## BMAD Agent Surface

Codex plugins deploy skills and files; they do not directly register native Codex subagents. Team Durham's deployable agent layer is bundled through BMAD Builder overrides:

| BMAD Agent | Team Durham Persona |
|------------|---------------------|
| `bmad-agent-pm` | Kotler |
| `bmad-agent-analyst` | Tufte |
| `bmad-agent-architect` | Aaker |
| `bmad-agent-dev` | Rand |
| `bmad-agent-tech-writer` | Ogilvy |
| `bmad-agent-ux-designer` | Glaser |

See `docs/BMAD-AGENTS.md` and use `$team-durham-bmad`.

## Operating Rules

- STP before pixels.
- Search before write.
- Brand truth is canonical once locked.
- QA is read-only: Munari flags, producers fix.
- Project-specific governance applies only to that project.
- Persona research grounds voice, but governance wins.

## Start Here

- `agents/brand-orchestrator.md`
- `source/codex/agents/kotler.md`
- `source/codex/governance/README.md`
- `source/codex/research/team-durham-persona-research.md`
- `commands/orchestrate.md`
- `source/bmad/custom/bmad-agent-pm.toml`
