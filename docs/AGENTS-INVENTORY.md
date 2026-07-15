# Agents Inventory

> Canonical six-team roster for the first sync pass across Notion, GitHub, and runtime manifests.

## Purpose

This inventory is the backbone for the agents lane. It records the team roster that Notion should present, the GitHub-side canonical names, and the runtime-facing group identifiers used by Claude and Codex.

## Canonical Teams

| Canonical name | Group ID | Function | Agent count | Status | Notes |
|---|---|---|---:|---|---|
| Team RAM | `allura-system` | Engineering harness | 10 | active | CLI harness used for architecture, code, infra, performance, and quality. |
| Team Durham | `allura-team-durham` | Brand delivery harness | 9 | active | Brand studio team for strategy, naming, visual direction, copy, QA, and memory. |
| Team Raleigh | `allura-raleigh` | Faith Meats operations | 15 | building | Operations, sales, and marketing package already modeled in `factory/teams/raleigh/team.yaml`. |
| Team Penasoto | `allura-penasoto` | Mortgage audit operations | 7 | packaged | Loan file QC, TRID, underwriting, investor guidelines, regulatory change, and privacy. |
| Team Charlotte | `allura-charlotte` | Difference Driven brand team | 6 | building | Present in the ecosystem context; needs the same canonical inventory treatment. |
| Bahari | `allura-bahari` | Curator / HITL gate | 5 | active | Shared governance lane, not a normal delivery team. |

## Sync Rules

- Notion owns the human-facing roster and team status.
- GitHub owns the canonical inventory doc and the package manifests that implement it.
- Runtime manifests must use the same canonical team names and group IDs.
- Bahari is documented as a curator lane, not a deployable delivery roster.
- The roster is not complete until each team has source-path evidence and a validation receipt.

## Source Evidence

- `factory/teams/raleigh/team.yaml`
- `factory/teams/penasoto/team.yaml`
- `allura-memory/project-context.md`
- `allura-memory/docs/allura/` canonical documentation tree

## Next Inventory Pass

After the agents roster is stable, mirror the same pattern for:

- Skills inventory
- Commands inventory
