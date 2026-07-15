# Allura Brain Memory Provider for Hermes

Bridges Hermes Agent's turn lifecycle to **Allura Brain** — governed memory with
PostgreSQL (episodic traces) + Neo4j (semantic, HITL-promoted) stores.

## What it does

- **Ambient recall** — `prefetch()` runs `memory_search` before each LLM call
- **Ambient persist** — `sync_turn()` writes a *concise outcome trace* after each turn
  (not raw transcript — respects Allura's curation model)
- **Deliberate tools** — `allura_recall`, `allura_remember`, `allura_governance_check`
- **Governance guard** — enforces `allura-*` namespace, blocks legacy tenants
- **Pre-compress extraction** — saves insights from messages about to be discarded

## Setup

### 1. Configure

```bash
hermes memory setup
# or edit ~/.hermes/allura-brain.json:
```

```json
{
  "brain_url": "http://127.0.0.1:5888/mcp",
  "group_id": "allura-system",
  "agent_id": "hermes-agent",
  "sync_mode": "outcomes_only"
}
```

| Field | Values | Default |
|-------|--------|---------|
| `brain_url` | Allura Brain MCP URL | `http://127.0.0.1:5888/mcp` |
| `group_id` | Tenant namespace (`allura-*`) | `allura-system` |
| `agent_id` | Hermes identity for writes | `hermes-agent` |
| `sync_mode` | `off` / `outcomes_only` / `full` | `outcomes_only` |

### 2. Activate

```yaml
# ~/.hermes/config.yaml
memory:
  provider: "allura-brain"
```

### 3. Verify

```bash
hermes allura-brain status   # reachability + config
hermes allura-brain test     # round-trip add + search
```

## Tools exposed to the model

| Tool | Maps to | Purpose |
|------|---------|---------|
| `allura_recall` | `memory_search` | Deliberate recall |
| `allura_remember` | `memory_add` | Deliberate persist |
| `allura_governance_check` | `governance_check_gate` | Pre-flight invariant check |

Deliberately **not** exposed: `memory_delete`, `memory_promote`, policy mutation —
those are curator/HITL operations, not agent-runtime.

## Governance

- `group_id` must match `allura-*`
- Blocks legacy: `allura-roninmemory`, `allura-team-ram`, `roninclaw-*`
- Default: `allura-system`

## Relationship to MCP server config

The existing `mcp_servers.allura_brain` entry in `config.yaml` stays available
for users who prefer explicit MCP tool calls. This provider is the *native
lifecycle integration*; the MCP server is the *manual escape hatch*.

## Requirements

- Allura Brain running at the configured URL (default `http://127.0.0.1:5888/mcp`)
- Hermes Agent v21+ (memory provider plugin support)