# Allura Plugins

Canonical, organization-owned plugin catalog for the Allura ecosystem.

This repository is the single source of truth for:
1. **Plugin marketplace** — validated Allura plugins for Claude Code and Codex CLI
2. **Model governance** — the `docs/models.yaml` registry mapping agents to models
3. **Cross-runtime scripts** — update, audit, eval, and performance tooling

## Status

**Active.** The catalog ships 3 plugins for Claude Code and Codex CLI.

## Marketplace

The `allura-ecosystem` Claude marketplace contains 3 plugins:

| Plugin | Version | Category | Description |
|--------|---------|----------|-------------|
| **allura-cowork** | 0.2.0 | Coordination | Shared Claude Code + Codex cowork protocol for Allura-governed collaboration, runtime honesty, validation, and handoff |
| **team-durham** | 0.2.0 | Design | Team Durham brand production team — 12 agents, ~70 skills, 21 commands, governance, persona research |
| **team-ram-coding** | 0.2.0 | Coding | Team RAM coding plugin for Allura-governed Brooks, Jobs, Scout, and Woz workflows — 12 agents, 34 commands, 13 skills |

### Install

```bash
# Claude Code (from marketplace)
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install allura-cowork@allura-ecosystem
/plugin install team-durham@allura-ecosystem
/plugin install team-ram-coding@allura-ecosystem

# Codex CLI
# Source in ~/plugins/<name>, register in ~/.agents/plugins/marketplace.json,
# enable as <name>@plugins-cli in ~/.codex/config.toml
```

### Update All Runtimes

```bash
./scripts/plugins-update-all.sh
```

## Model Governance

The [`docs/models.yaml`](docs/models.yaml) registry maps agents to models across runtimes.

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/models-update-all.sh` | Sync agent frontmatter to registry. Drift detection. **Dry-run first.** |
| `scripts/models-eval.sh` | CLASSIC eval framework against fixtures. |
| `scripts/models-performance.sh` | Aggregate `MODEL_INVOKED` events from Allura Brain. |
| `scripts/commands-audit.sh` | Audit orphans, format drift, missing frontmatter, command collisions. |
| `scripts/plugins-update-all.sh` | Update plugins across runtimes. |

## Plugins in this Repo

```
allura-plugins/
├── .claude-plugin/marketplace.json   # Claude marketplace (3 plugins)
├── allura-cowork/                    # Cowork protocol plugin
├── team-durham/                      # Team Durham brand harness
├── team-ram-coding/                  # Team RAM coding plugin
├── docs/
│   └── models.yaml                   # Model governance registry
├── scripts/                          # Update, audit, eval scripts
└── evals/
    └── fixtures/                     # CLASSIC eval fixtures
```

## License

MIT — see [LICENSE](LICENSE).