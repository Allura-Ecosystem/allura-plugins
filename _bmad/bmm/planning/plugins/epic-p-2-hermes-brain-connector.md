# Epic P-2 — Hermes Allura Brain Connector

**Status:** Planned
**Owner:** Brooks (architecture) + Woz (implementation)
**Tenant:** allura-system
**Repo:** `plugins/allura-plugins/plugins/hermes-allura-brain/`

## Goal

Ship a typed, tenant-scoped Hermes-native provider that lets Hermes subagents query Allura Brain before starting work and write outcomes back after completing—with authentication, tenant propagation, and degraded-state handling.

## Product Boundary

The connector is a narrow memory-provider surface. It exposes governed recall and outcome persistence. It does not expose curator or governance mutations. Tenant scope is inherited from trusted delegation context, never self-asserted by a subagent.

## Current State

- Hermes-native provider exists in `plugins/hermes-allura-brain/`.
- Its native `plugin.yaml` is catalog-validated as `allura-brain` v0.2.0.
- Typed contract, delegation tenant propagation, and health/retry behavior remain planned delivery work.

## Story Map

| Story | Outcome | Dependency | Ship condition |
|---|---|---|---|
| P-2.1 | Connector contract — typed memory-provider surface | — | Recall and outcome-write inputs are typed, validated, and documented |
| P-2.2 | Authentication and tenant scoping — group_id propagation | P-2.1 | group_id inherited from delegation context; cross-tenant access denied |
| P-2.3 | Connection health and retry — degraded-state handling | P-2.1 | Brain-down detected; bounded retry; degraded state surfaced |

## Dependencies

- Allura Brain MCP server (Allura_Memory)
- Hermes delegation framework

## Rollback

Disable the provider. Hermes falls back to its configured memory behavior without affecting Allura Brain.
