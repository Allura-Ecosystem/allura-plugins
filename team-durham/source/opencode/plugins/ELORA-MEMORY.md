# Elora / Allura Shared Memory

For Team Durham, "Elora" is treated as the shared Allura Brain memory layer unless a separate Elora runtime is explicitly configured.

Shared memory contract:

- `group_id`: `allura-team-durham`
- Primary OpenCode tools: `allura-brain_memory_search`, `allura-brain_memory_list`, `allura-brain_memory_add`
- Codex MCP aliases: `mcp__allura_brain__memory_search`, `mcp__allura_brain__memory_list`, `mcp__allura_brain__memory_add`
- Every agent searches shared memory before acting.
- Every meaningful decision/outcome is logged after work.
- Brand truth and promoted decisions are not overwritten; they are superseded with evidence.

Each callable agent in `.opencode/agents/` contains:

- an agent-specific `user_id`
- the shared `group_id`
- an activation instruction to hydrate from Allura Brain/shared memory
- a pointer back to its canonical `.claude/agents/*.md` definition

