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

## Package Contract

### Native provider manifest

This is a Hermes-native provider, declared by `plugin.yaml` as
`allura-brain` version `0.2.0`. It is not a Claude marketplace package and does
not implement the Claude/Codex package-manifest contract.

### Validation

Run `python3 scripts/validate_manifests.py` from the catalog root for native
manifest and package-contract validation. In a Hermes runtime, use
`hermes allura-brain test` for the authenticated, read-only provider check.

### Dependencies and degraded behavior

The provider requires the three secret-scope values listed above and the
canonical public MCP tunnel. Without them it remains unavailable; it does not
fall back to a local endpoint or report ambient recall/persistence as complete.
