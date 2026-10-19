# Allura Marketplace IDs and Native Plugin Identities

Updated: 2026-10-13

Catalog identities describe distribution surfaces, not what is installed or running
on a particular machine. Standalone sources own plugin content and versions;
`source-locks.json` identifies this catalog's generated exports.

## Portable marketplace packages

| Catalog alias | Source manifest identity | Catalog version | Surface |
|---|---|---|---|
| `allura-cowork` | `allura-cowork` | 0.3.0 | Claude/Codex portable plugin |
| `team-durham` | `team-durham` | 0.4.0 | Claude/Codex generated plugin |
| `team-ram-coding` | `team-ram-harness` | 0.5.0 | Claude/Codex generated plugin |
| `bumblebee` | `bumblebee` | 0.1.1 | Claude/Codex generated plugin |

The Claude marketplace is `allura-ecosystem`, declared by
[`.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json). For example:

```text
/plugin install team-ram-coding@allura-ecosystem
/plugin install team-durham@allura-ecosystem
```

Codex's repository catalog is
[`.agents/plugins/marketplace.json`](../.agents/plugins/marketplace.json); package
metadata uses `.codex-plugin/plugin.json`. Verify installation through the host's
supported plugin flow. These manifests do not establish a particular user's enabled
plugins, cache locations, or current-session capabilities.

`team-ram-harness` is the source-owned identity inside `team-ram-coding/`, not a
second root marketplace entry. Do not create another manual package copy to resolve
the compatibility alias.

## Native and other package identities

| Package | Runtime identity | Version / state | Distribution |
|---|---|---|---|
| [Hermes Allura Brain](../plugins/hermes-allura-brain/README.md) | `allura-brain` | Catalog 0.2.0 | Native Hermes memory provider |
| [Hermes Team RAM + Durham](https://github.com/Allura-Ecosystem/hermes-team-ram-durham) | `team-ram-durham` | 1.1.0 local validation release; publication pending | External native Hermes plugin, not a catalog-generated export |
| [Mortagate Cowork](../packages/mortagate-cowork/README.md) | `packages/mortagate-cowork` | Catalog 0.2.1 | Microsoft Cowork package |

These packages are absent from the portable Claude/Codex marketplaces. The native
Hermes team link does not claim that a remote install already provides version
`1.1.0`; consult the source release evidence before installing that release.

### Hermes team usage in 1.1.0

```text
/ram <task>
/durham <task>
/ram-woz <task>
/durham-copywriter <task>
```

The native `allura_team` tool loads the selected role and adaptive workflow into
the current conversation. The active agent performs the task using its configured
model and existing permissions. There is no model override or worker subprocess;
guidance loading alone is not execution evidence.

Slash commands queue work through the installed CLI's injection support. Gateway
surfaces without injection support report that the task has not started. Send a
normal prompt asking the active agent to use `allura_team` with the desired `team`,
`role`, and `task`, then continue in the current conversation.

Skills register actual files as `team-ram-durham:ram-<name>` or
`team-ram-durham:durham-<name>`, avoiding collisions between the teams' skill names.
The entry workflows are `team-ram-durham:ram` and `team-ram-durham:durham`.

The [Allura Brain provider](../plugins/hermes-allura-brain/README.md) remains
separate. The team plugin neither replaces nor reconfigures that provider. Every
Brain operation specifies a tenant: `allura-system` for RAM and
`allura-team-durham` for Durham. If that scope is unavailable, report degraded
local-only context rather than silently using a provider default.

## Source-first update workflow

Default invocation and `--dry-run` perform read-only local catalog metadata,
manifest, and model audits:

```bash
bash scripts/plugins-update-all.sh
bash scripts/plugins-update-all.sh --dry-run
```

Use committed local sources to verify exact locked exports without an upstream
fetch. A package selector is a source ID or compatibility alias:

```bash
bash scripts/plugins-update-all.sh --dry-run --package team-ram \
  --source team-ram=/path/to/allura-team-ram
```

Repeat `--package` and `--source` for other exports. In audit mode, every selected
export needs a local source binding. Without `--source`, only local catalog checks
run; pinned source content is not reverified.

Explicit sync regenerates repository exports and metadata, then audits the result:

```bash
bash scripts/plugins-update-all.sh --sync --package team-ram \
  --source team-ram=/path/to/allura-team-ram
```

`--sync` may fetch locked remote source repositories when local bindings are omitted.
It never installs runtime plugins, clears caches, pulls installed marketplaces,
restarts gateways, or rewrites user configuration. `--runtime` and installation
flags are unsupported. The external Hermes team plugin is maintained in its own
source repository and is not installed by this command.

Publish source commits separately before expecting remote consumers to resolve new
pins. Failed source or catalog audits return errors rather than an update-success
message. Use `--help` for supported options.

## Ownership rules

- Make content and model-binding changes in canonical source; regenerate pinned exports.
- Keep portable marketplace identities separate from native runtime identities.
- Verify actual installation and execution in the intended runtime before claiming readiness.
- Preserve scoped Brain access and required human approvals across every runtime.
