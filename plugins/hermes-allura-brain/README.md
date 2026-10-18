# Allura Brain Memory Provider for Hermes

Native Hermes memory-provider integration for Allura Brain. It complements the
full native MCP server connection with lifecycle behavior:

- recalls relevant explicitly configured tenant context before planning;
- writes concise, sanitized outcomes after substantive primary-agent turns;
- exposes `allura_recall`, `allura_remember`, and `allura_governance_check`;
- refuses legacy tenants and non-canonical endpoints;
- uses only `https://mcp.faithmeats.org/mcp`.

## Required secret-scope values

Configure these through Hermes Secrets/Bitwarden or the active profile's
`.env`; never put their values in `config.yaml` or this repository:

- `ALLURA_MCP_TOKEN`
- `ALLURA_CF_ACCESS_CLIENT_ID`
- `ALLURA_CF_ACCESS_CLIENT_SECRET`

The generic token has priority. For compatibility, only an explicit
`allura-system` profile can use `ALLURA_MCP_TROY_DESKTOP_TOKEN`, and only an
explicit `allura-faithmeats` profile can use `ALLURA_MCP_TROY_ADMIN_TOKEN`.
There is no desktop-to-admin fallback and no fallback for other tenants.

## Non-secret profile config

`$HERMES_HOME/allura-brain.json` must contain an explicit authorized `group_id`
matching `^allura-[a-z0-9-]+$`. There is no tenant default. Set the active profile
path deliberately; existing explicit tenants remain unchanged. This example is
only for a profile authorized for `allura-faithmeats`:

```json
{
  "brain_url": "https://mcp.faithmeats.org/mcp",
  "group_id": "allura-faithmeats",
  "sync_mode": "outcomes_only",
  "timeout": 30
}
```

Missing/malformed configuration makes the provider unavailable. A different
per-call tenant is rejected locally. Historical `agent_id` settings are ignored;
authenticated transport owns identity. Writes send only `source` and
`conversation_id` metadata; semantic promotion remains human governed.

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
`allura-brain` version `0.3.0`. It is not a Claude marketplace package and does
not implement the Claude/Codex package-manifest contract.

### Validation

Run `python3 scripts/validate_manifests.py` from the catalog root for native
manifest and package-contract validation. In a Hermes runtime, use
`hermes allura-brain test` for the authenticated, read-only provider check.

### Dependencies and degraded behavior

The provider requires the three secret-scope values listed above and the
canonical public MCP tunnel. Without them it remains unavailable; it does not
fall back to a local endpoint or report ambient recall/persistence as complete.

## Context reuse across team work

Pass a compact recall receipt to authorized workers in the same project and tenant
instead of asking every persona to repeat the same retrieval. Record query,
retrieval time, source IDs and task scope; refresh changed or contradictory facts.
Authorization and live governance checks still run at the protected operation.
This is orchestration guidance; this provider does not implement a cross-session
cache or choose models. No model or runtime configuration changes are performed by this source release.
