# Allura Brain Memory Provider for Hermes

Native Hermes memory-provider integration for Allura Brain. It complements the
full native MCP server connection with lifecycle behavior:

- recalls relevant `allura-faithmeats` context before planning;
- writes concise, sanitized outcomes after substantive primary-agent turns;
- exposes `allura_recall`, `allura_remember`, and `allura_governance_check`;
- refuses legacy tenants and non-canonical endpoints;
- uses only `https://mcp.faithmeats.org/mcp`.

## Required secret-scope values

Configure these through Hermes Secrets/Bitwarden or the active profile's
`.env`; never put their values in `config.yaml` or this repository:

- `ALLURA_MCP_TROY_ADMIN_TOKEN`
- `ALLURA_CF_ACCESS_CLIENT_ID`
- `ALLURA_CF_ACCESS_CLIENT_SECRET`

## Non-secret profile config

`$HERMES_HOME/allura-brain.json`:

```json
{
  "brain_url": "https://mcp.faithmeats.org/mcp",
  "group_id": "allura-faithmeats",
  "agent_id": "troy-admin",
  "sync_mode": "outcomes_only",
  "timeout": 30
}
```

Activate with:

```bash
hermes plugins enable allura-brain
hermes config set memory.provider allura-brain
hermes allura-brain status
hermes allura-brain test
```

The test command performs an authenticated read-only search. It never prints
credential values and does not create test memories.
