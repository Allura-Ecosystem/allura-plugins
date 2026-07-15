# Sync Control Plane

> Working design for keeping Claude and Codex aligned across agents, skills, and commands.

## Goal

Keep the Allura ecosystem synchronized without pretending Claude and Codex have the same runtime mechanics.

The sync target is:

- the same approved capability set where parity is possible
- the same canonical naming and ownership model
- the same validation and approval gates

The sync target is not:

- identical plugin internals
- identical runtime configuration files
- a single shared install surface for both runtimes

## Authority Model

There are four layers of authority:

1. Notion is the human control plane.
2. GitHub pull requests are the approval gate.
3. `allura-plugins` is the release catalog.
4. Runtime installs are the last-mile surfaces for Claude and Codex.

`allura-memory` remains the canon for team models, governance rules, and routing contracts.

## Inventories

The sync model uses three separate inventories.

### Agents

Agents are the core roster. They define who exists, what team they belong to, what runtime(s) they support, and whether they are active, building, or retired.

Canonical team scope for the first release:

- Team RAM
- Team Durham
- Team Raleigh
- Team Penasoto
- Team Charlotte
- Bahari

### Skills

Skills are reusable method bundles. They should be tracked separately so platform parity does not get mixed with agent identity.

### Commands

Commands are runtime actions, launch flows, and operator helpers. They vary more by platform than agents do, so they need their own registry.

## Recommended Release Shape

Use one release lane for each inventory:

- Agents registry
- Skills registry
- Commands registry

Each lane should carry:

- canonical name
- owner
- platform support
- source path
- validation evidence
- status

## Sync Flow

1. Capture the canonical roster in Notion.
2. Mirror the roster into the GitHub inventory docs.
3. Package or update the runtime-specific manifest files.
4. Validate Claude and Codex independently.
5. Open a reviewable pull request.
6. Merge only after the evidence matches the canonical roster.
7. Publish the approved package set to runtime install surfaces.

## Validation Rules

- A roster item is not synced until both the canonical source and the runtime manifest agree.
- A package is not synced until it passes its runtime validation gate.
- A team is not synced until its Notion record, GitHub inventory, and runtime manifest all point at the same canonical name.
- Bahari is treated as a curator/gate function, not as a normal delivery team.

## Initial Evidence Target

The first completed agents pass should prove that these teams are present and mapped cleanly:

- Team RAM
- Team Durham
- Team Raleigh
- Team Penasoto
- Team Charlotte
- Bahari

Once agents are stable, apply the same pattern to skills and commands.
