# Allura Brain for Hermes

Connect Hermes to authorized project memory: recall relevant context before work and save concise outcomes after substantive turns.

This native provider complements a full Allura MCP connection. It exposes `allura_recall`, `allura_remember`, and `allura_governance_check`, using the configured tenant and authenticated identity. It connects only to `https://mcp.faithmeats.org/mcp`.

## Install

Select the intended Hermes profile, then install from a committed catalog checkout:

```bash
git clone --branch main --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
hermes plugins install "file://$(pwd)#plugins/hermes-allura-brain" --no-enable
```

`--no-enable` leaves activation for the configuration step below. Selecting this provider changes the profile's memory provider, so review the existing setting before activation.

## Configure access

### Required secret-scope values

Store these in Hermes Secrets/Bitwarden or the active profile's `.env`. Keep their values out of `config.yaml` and this repository.

- `ALLURA_MCP_TOKEN`
- `ALLURA_CF_ACCESS_CLIENT_ID`
- `ALLURA_CF_ACCESS_CLIENT_SECRET`

The generic token has priority. For compatibility, an explicitly configured `allura-system` profile can use `ALLURA_MCP_TROY_DESKTOP_TOKEN`; an explicitly configured `allura-faithmeats` profile can use `ALLURA_MCP_TROY_ADMIN_TOKEN`. There is no desktop-to-admin fallback or fallback for other tenants.

### Non-secret profile config

Create `$HERMES_HOME/allura-brain.json` in the intended active profile. `group_id` must name an authorized tenant and match `^allura-[a-z0-9-]+$`. The provider has no tenant default.

This example applies only to a profile authorized for `allura-faithmeats`:

```json
{
  "brain_url": "https://mcp.faithmeats.org/mcp",
  "group_id": "allura-faithmeats",
  "sync_mode": "outcomes_only",
  "timeout": 30
}
```

A valid tenant name alone grants no access. Missing or malformed configuration makes the provider unavailable; a different per-call tenant is rejected locally. Authenticated transport supplies identity, and historical `agent_id` settings are ignored.

## Activate and check

Once the profile's tenant and secrets are configured, deliberately select Allura Brain as its memory provider:

```bash
hermes plugins enable allura-brain
hermes config set memory.provider allura-brain
hermes allura-brain status
hermes allura-brain test
```

The test performs an authenticated read-only search. It does not create a test memory or print credential values. A successful search establishes that operation's result; it does not prove a later write succeeded.

## Memory behavior

The provider attempts relevant recall before planning and concise, sanitized outcome persistence after substantive primary-agent turns. The default `outcomes_only` mode retains a bounded summary rather than a full transcript. Supported modes are `off`, `outcomes_only`, and `full`; choose retention deliberately. Writes send `source` and `conversation_id` metadata. Semantic promotion remains subject to human review.

Workers on the same authorized task can reuse a fresh recall receipt containing the query, retrieval time, source IDs, and scope. Refresh changed or contradictory facts. This is coordination guidance; the provider does not implement a cross-session cache or choose models.

## Package Contract

### Native provider manifest

`plugin.yaml` declares the Hermes identity `allura-brain`, version `0.3.0`. This is a native Hermes provider, not a Claude or Codex marketplace package.

### Validation

From the catalog root, run `python3 scripts/validate_manifests.py` for manifest and package-contract checks. In a configured Hermes profile, run `hermes allura-brain test` for the authenticated read-only check.

### Dependencies and degraded behavior

The provider needs an explicit authorized tenant, the required secrets, and access to the canonical public MCP tunnel. Missing access leaves it unavailable; failures do not authorize another tenant, identity, credential, or local endpoint. Report recall and persistence only when their actual results support those claims.
