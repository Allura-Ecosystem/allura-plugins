# Codex Skill Bridge

Codex uses the shared Team Durham skill library at:

```text
../.agents/skills/
```

Before creating or revising any legend-based skill, read:

```text
../.Codex/research/team-durham-persona-research.md
```

Also read the governance bridge:

```text
../.Codex/governance/README.md
```

Skills should encode repeatable methods. Agent files carry voice and personality. A skill may include persona grounding, but it should not rely on imitation alone.

Important brand-production skills include:

- `client-brief-intake`
- `brand-strategy`
- `naming-pack`
- `copy-pack-assembler`
- `logo-direction-generator`
- `fal-ai-image-prompt-engineering`
- `fal-ideogram-executor`
- `brand-kit-10-section`
- `brand-consistency-review`
- `brand-presentation-builder`
- `design-tokens`
- `accessibility-aaa`
- `asset-first-design`
- `impeccable`
- `penpot-create-board`
- `penpot-foundations`
- `penpot-upload-media`
- `penpot-implement-mockups`
- `penpot-export-handoff`
- `allura-memory-skill`
- `memory-client`
- `global-mcp-lookup`
- `mcp-docker`
- `mcp-docker-memory`
- `mcp-libre`
- `workspace-guide`
- `task-management`

When updating a shared skill, update `../.agents/skills/{skill}/SKILL.md` first, then sync tool-specific copies under `../.claude/skills/` or `../.opencode/skills/` only if those adapters need them.
