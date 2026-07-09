# Codex Governance Bridge — Brand Maker / Allura / Project Rules

This file defines the governance order Codex must use before creating skills, editing agent behavior, or touching brand assets.

Brand Maker is a whole design team and multi-client brand production system. Project-specific rules, including RuVix/theDerm rules, apply only when that project or surface is explicitly in scope.

## Authority Order

1. `../GOVERNANCE.json`
   - Repo-level enforcement rules.
   - Gates brand asset edits, brand-truth access, color validation, agent permissions, and Munari pre-commit review.

2. `../.claude/agents/BRAIN-CONNECTION.md`
   - Mandatory Allura Brain connection and logging protocol.
   - Requires `group_id = allura-team-durham`, search before write, Postgres first, Neo4j only after validation.

3. `../.claude/skills/allura-memory-skill/SKILL.md`
   - Memory behavior contract.
   - Governs raw trace vs curated insight, promotion, superseding, deprecation, and conflict handling.

4. `../.claude/rules/agent-routing.md`
   - Team Durham routing and role boundaries.

5. Client/project files under `../clients/{client}/`
   - Client brief, strategy pack, brand-truth, kit, QA, assets, and delivery artifacts.
   - These define the active brand's local truth.

6. Project-specific rules
   - Example: `../.claude/rules/allura-dashboard-branding.md`.
   - Apply only when the active task is that project/surface.

7. `../.Codex/research/team-durham-persona-research.md`
   - Persona grounding for legend-inspired agents.
   - Shapes voice and method, but never overrides governance.

## Skill Creation Gate

Before creating or revising a Team Durham skill:

1. Read the relevant persona note in `../.Codex/research/team-durham-persona-research.md`.
2. Read `../GOVERNANCE.json`.
3. Identify the active client/project and read its local source files under `../clients/{client}/` when applicable.
4. If a project-specific governance rule exists for that project, read it before acting.
5. If the skill stores, retrieves, promotes, supersedes, or deletes memory, read `../.claude/skills/allura-memory-skill/SKILL.md`.
6. If the skill changes routing, handoffs, permissions, or agent responsibilities, read `../.claude/rules/agent-routing.md`.

## Project-Scoped Rules

RuVix/theDerm-style rules are not global Team Durham rules. They are project gates.

Use them only when:

- The user names that project.
- The active workspace/client is that project.
- A file being edited belongs to that project.
- A command/runbook explicitly invokes that project gate.

When a project-specific rule applies:

- Treat it as binding for that project.
- Do not apply it to unrelated clients.
- Do not let it overwrite Team Durham's general brand-production pipeline.
- Record the source rule and evidence used in the handoff.

Current known project-specific rule in this repo:

- `../.claude/rules/allura-dashboard-branding.md` — scoped to Allura Dashboard surfaces only. The Captain has clarified this is not the global design-team rule and should be treated as project/surface-specific, similar to how RuVix/theDerm rules would be scoped.

## Brand Governance Non-Negotiables

From `GOVERNANCE.json`:

- Search Allura Brain for brand truth before editing brand assets.
- Hardcoded colors in governed files must match `brand-truth.json` primitives or approved tokens.
- `brand-truth.json` and derived tokens are canonical and read-only; changes require supersede requests and HITL approval.
- Munari is read-only. QA flags issues; producing agents fix.
- Brand asset commits require Munari gate review.

## Practical Rule

Personality makes agents distinct. Skills make work repeatable. Governance decides what is permissible. Project rules bind only the project they belong to.

If these conflict, governance wins.
