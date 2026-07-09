# Codex Adapter — Team Durham

This directory lets Codex co-work with the Team Durham design system without duplicating the canonical harness.

## Source Of Truth

- Canonical agents: `../.claude/agents/*.md`
- Shared skills: `../.agents/skills/*/SKILL.md`
- Canonical commands: `../.claude/commands/*.md`
- Persona research: `research/team-durham-persona-research.md`
- Governance bridge: `governance/README.md`
- Codex manifest: `config/team-durham.json`
- Legacy OpenCode adapter: `../.opencode/`

Do not fork agent behavior into `.Codex/agents/` unless a Codex-specific wrapper is genuinely required. Edit `.claude/agents/{agent}.md` first, then update adapters that need frontmatter or command shims.

## Operating Mode

When a user asks for brand/design production work, activate Team Durham as the working model:

1. Kotler frames intent, constraints, phase, and handoff.
2. Aaker owns strategy, STP, and `brand-truth.json` sign-off.
3. Ogilvy owns naming, copy, messaging, and voice.
4. Glaser owns visual direction, logo exploration, and image generation prompts.
5. Rand owns complete brand kit assembly.
6. Munari reviews quality read-only and routes fixes back to the producing agent.
7. Tufte handles research, evidence, and data-heavy brand decisions.
8. Scout, Reality Checker, Evidence Collector, Workflow Architect, and Agentic Trust Architect support discovery, proof, workflow, and governance.

## Non-Negotiables

- Use `group_id = 'allura-team-durham'` for Allura Brain operations.
- Governance before persona: `GOVERNANCE.json`, Brain connection rules, Allura Memory rules, and active client/project rules override agent personality and skills.
- Project-specific gates such as RuVix/theDerm apply only when that project or surface is active; do not treat them as global Team Durham rules.
- Research before skill creation: do not create or revise a legend-based skill until the relevant note in `research/team-durham-persona-research.md` has been read and updated if needed.
- STP before pixels: do not start visual/Penpot work until Aaker's strategy gate is locked.
- QA is read-only: Munari flags issues but does not directly fix production deliverables.
- Vision-critical work must inspect actual image files, not only filenames or metadata.
- Prefer shared skills in `../.agents/skills/`; use `.claude/skills/` or `.opencode/skills/` only when a tool-specific copy is required.

## Agent Index

| Agent | Persona | Canonical File |
|-------|---------|----------------|
| Brand Orchestrator | Philip Kotler | `../.claude/agents/brand-orchestrator.md` |
| Brand Strategist | Jennifer Aaker | `../.claude/agents/brand-strategist.md` |
| Visual Director | Milton Glaser | `../.claude/agents/visual-director.md` |
| Copywriter | David Ogilvy | `../.claude/agents/copywriter.md` |
| Brand Kit Builder | Paul Rand | `../.claude/agents/brand-kit-builder.md` |
| QA Reviewer | Bruno Munari | `../.claude/agents/qa-reviewer.md` |
| Data Analyst | Edward Tufte | `../.claude/agents/data-analyst.md` |
| Scout Recon | Utility | `../.claude/agents/scout-recon.md` |
| Reality Checker | Allura Ops | `../.claude/agents/reality-checker.md` |
| Evidence Collector | Allura Ops | `../.claude/agents/evidence-collector.md` |
| Workflow Architect | Allura Ops | `../.claude/agents/workflow-architect.md` |
| Agentic Trust Architect | Allura Ops | `../.claude/agents/agentic-trust-architect.md` |
| OpenAgent | Fallback | `../.claude/agents/openagent.md` |
