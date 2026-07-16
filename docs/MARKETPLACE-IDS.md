# Allura Marketplace IDs — Cross-Runtime Plugin Registry

**Last updated:** 2026-07-16
**Author:** Brooks (Chief Architect)
**Status:** Active

This document maps every Allura plugin to its marketplace ID across all 4 runtimes: Claude, Codex, Hermes, and OpenClaw.

---

## Runtime Summary

| Runtime | Marketplace concept | Plugin format | Install | Update |
|---|---|---|---|---|
| **Claude** | `marketplace.json` + `known_marketplaces.json` | `.claude-plugin/plugin.json` | `claude plugin install <name>@<marketplace>` | `/plugin update` or `plugins-update-all.sh` |
| **Codex** | `plugins-cli` (built-in cache) + `~/.agents/plugins/marketplace.json` | `.codex-plugin/plugin.json` | config.toml `[plugins."<name>@plugins-cli"]` | config edit or `plugins-update-all.sh` |
| **Hermes** | Git repo (`hermes plugins install user/repo`) | `plugin.yaml` + `__init__.py` | `hermes plugins install <owner>/<repo> --enable` | `hermes plugins update <name>` |
| **OpenClaw** | ClawHub / npm / git / local path | `openclaw.plugin.json` (native) or compatible bundle | `openclaw plugins install <source>:<package>` | `openclaw plugins update <id>` + `openclaw gateway restart` |

---

## Plugin Registry

### allura-cowork
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | `allura-ecosystem` | 0.1.0 | `claude plugin install allura-cowork@allura-ecosystem` |
| Codex | `plugins-cli` | 0.1.0 | `[plugins."allura-cowork@plugins-cli"] enabled = true` in `~/.codex/config.toml` |
| Hermes | — | — | Not applicable (Claude/Codex plugin) |
| OpenClaw | — | — | Not yet installed. Compatible bundle: `openclaw plugins install ./allura-plugins/allura-cowork` |

### team-durham
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | `allura-ecosystem` | 0.1.0 | `claude plugin install team-durham@allura-ecosystem` |
| Codex | `plugins-cli` | 0.1.0 | `[plugins."team-durham@plugins-cli"] enabled = true` |
| Hermes | — | — | Not applicable |
| OpenClaw | — | — | Not yet installed. Compatible bundle: `openclaw plugins install ./allura-plugins/team-durham` |

### team-ram-coding
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | `allura-ecosystem` | 0.1.0+codex | `claude plugin install team-ram-coding@allura-ecosystem` |
| Codex | `plugins-cli` | 0.1.0+codex | `[plugins."team-ram-coding@plugins-cli"] enabled = true` |
| Hermes | — | — | Not applicable |
| OpenClaw | — | — | Not yet installed |

### team-ram-harness
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | `allura-ecosystem` + `team-ram-marketplace` (legacy) | 0.4.2 | `claude plugin install team-ram-harness@allura-ecosystem` |
| Codex | `plugins-cli` | 0.4.2 | `[plugins."team-ram-harness@plugins-cli"] enabled = true` |
| Hermes | — | — | Not applicable |
| OpenClaw | — | — | Not yet installed. Compatible bundle: `openclaw plugins install ./Agent-Harnesses/Allura-TeamRam` |

### allura (Codex-only)
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | — | — | No `.claude-plugin/` manifest — Codex-only |
| Codex | `plugins-cli` | 0.1.0 | `[plugins."allura@plugins-cli"] enabled = true` |
| Hermes | — | — | Not applicable |
| OpenClaw | — | — | Not yet installed |

### team-ram-payload (Codex-only)
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | — | — | No `.claude-plugin/` manifest — Codex-only |
| Codex | `plugins-cli` | 0.1.0 | `[plugins."team-ram-payload@plugins-cli"] enabled = true` |
| Hermes | — | — | Not applicable |
| OpenClaw | — | — | Not yet installed |

### hermes-allura-brain (Hermes-only)
| Runtime | Marketplace ID | Version | Install command |
|---|---|---|---|
| Claude | — | — | Not applicable (Hermes plugin) |
| Codex | — | — | Not applicable |
| Hermes | Git repo | 0.1.0 | `hermes plugins install Charitablebusinessronin/hermes-allura-brain --enable` then `hermes config set memory.provider allura-brain` |
| OpenClaw | — | — | Not applicable |

**Note:** `hermes-allura-brain` is a **memory provider** (single-select), activated via `memory.provider` in `~/.hermes/config.yaml`, NOT via `plugins.enabled`. Update with `hermes plugins update allura-brain`. Verify with `hermes allura-brain status`.

---

## Codex `plugins-cli` Marketplace

**What it is:** `plugins-cli` is the Codex CLI's built-in plugin cache/marketplace. It is not a remote registry — it's a local cache at `~/.codex/plugins/cache/plugins-cli/`.

**Install pattern (from Codex memories):**
1. Install plugin source under `/home/ronin704/plugins/<name>/`
2. Register in `~/.agents/plugins/marketplace.json`
3. Enable in `~/.codex/config.toml`: `[plugins."<name>@plugins-cli"] enabled = true`

**Current Codex plugins enabled:**
- `allura-cowork@plugins-cli`
- `superpowers@plugins-cli`
- `team-ram-core@plugins-cli` (note: name differs from Claude's `team-ram-harness`)
- `team-durham@plugins-cli`
- `team-ram-coding@plugins-cli`

**Name drift:** Codex uses `team-ram-core` while Claude uses `team-ram-harness`. These refer to the same plugin. The `plugins-update-all.sh` script handles both names.

---

## OpenClaw Compatible-Bundle Path

OpenClaw supports a **compatible bundle** format — it maps Codex/Claude/Cursor plugin layouts into OpenClaw inventory without requiring a native `openclaw.plugin.json`.

**Install a Claude/Codex plugin into OpenClaw:**
```bash
openclaw plugins install ./allura-plugins/<name>      # local path
openclaw plugins install --link ./allura-plugins/<name>  # symlink for dev
```

**After install:**
```bash
openclaw plugins enable <plugin-id>
openclaw gateway restart
openclaw plugins inspect <plugin-id> --runtime --json   # verify
```

**Limitation:** Compatible bundles expose skills, commands, and hooks — but not OpenClaw-specific runtime capabilities (channels, model providers, image/video gen). For those, write a native `openclaw.plugin.json`.

**Current state:** No Allura plugins installed in OpenClaw yet (7/69 stock plugins enabled).

---

## Update Workflow

**Single command to update all plugins across all runtimes:**
```bash
bash allura-plugins/scripts/plugins-update-all.sh
```

**Options:**
```bash
--dry-run                # preview only, no writes
<plugin-name>            # update one plugin
--runtime <runtime>      # filter by runtime (claude|codex|hermes|openclaw)
```

**What the script does:**
1. Scans all plugin manifests (`.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `plugin.yaml`, `openclaw.plugin.json`)
2. Syncs versions into marketplace.json files
3. Calls runtime-specific update commands (`hermes plugins update`, `openclaw plugins update`)
4. Clears stale Claude cache entries
5. Git-pulls git-source marketplaces
6. Prints a summary table

---

## Marketplace Registry (Claude `known_marketplaces.json`)

| Marketplace | Source | Type |
|---|---|---|
| `allura-ecosystem` | `allura-plugins/` (directory) | Primary — all Claude plugins |
| `team-ram-marketplace` | `Agent-Harnesses/Allura-TeamRam` (directory) | Legacy fallback for team-ram-harness |
| `allura-local` | `github.com/Charitablebusinessronin/Allura_Memory.git` (git) | Legacy fallback |
| `team-durham-local` | `github.com/Charitablebusinessronin/team_durham` (git) | Legacy fallback |
| `claude-plugins-official` | `github.com/anthropics/claude-plugins-official` (git) | Third-party |
| `harness-marketplace` | `github.com/revfactory/harness` (git) | Third-party |
| `superpowers-dev` | `github.com/obra/superpowers` (git) | Third-party |

---

## Rules

1. **One primary marketplace** — `allura-ecosystem` is the primary marketplace for all Allura Claude plugins. Per-plugin marketplaces are legacy fallbacks.
2. **Version sync** — `plugins-update-all.sh` keeps marketplace.json versions in sync with plugin.json versions. Never hand-edit marketplace versions.
3. **Cross-runtime awareness** — the update script handles all 4 runtimes. A plugin may exist in 1, 2, 3, or all 4 runtimes.
4. **Hermes memory provider** — activated via `memory.provider` config, not `plugins.enabled`. Do not call `hermes plugins enable` for it.
5. **OpenClaw gateway restart** — required after any OpenClaw plugin update. The script does this automatically.
6. **group_id on every Brain operation** — `allura-system` for RAM, `allura-team-durham` for Durham.