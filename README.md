# Allura Plugins

Canonical, organization-owned plugin catalog and **model governance registry** for the Allura ecosystem.

This repository is the single source of truth for:
1. **Plugin marketplace** — validated Allura plugins for Claude, Codex, Hermes, and OpenClaw
2. **Model governance** — the `models.yaml` registry that maps every agent to its model across all runtimes
3. **Cross-runtime scripts** — update, audit, eval, and performance tooling

Home directories are installation and cache surfaces, not authoring authorities.

## Status

**Active.** The catalog is populated with 4 plugins, a model governance registry covering 47 agents across 4 runtimes, and cross-runtime update/audit/eval scripts.

## Marketplace

The `allura-ecosystem` Claude marketplace contains 4 plugins:

| Plugin | Version | Category | Description |
|--------|---------|----------|-------------|
| **allura-cowork** | 0.1.0 | Coordination | Shared Claude Code + Codex cowork protocol for Allura-governed collaboration, runtime honesty, validation, and handoff |
| **team-durham** | 0.1.0 | Design | Team Durham brand production team — agents, skills, commands, governance, persona research |
| **team-ram-coding** | 0.1.0+codex | Coding | Team RAM coding plugin for Allura-governed Brooks, Jobs, Scout, and Woz workflows |
| **team-ram-harness** | 0.4.2 | Coding | Team RAM OpenCode Harness — self-evolving multi-agent orchestration with 10 specialists, SONA learning, coherence monitoring, HITL governance |

### Install

```bash
# Claude Code (from marketplace)
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install allura-cowork@allura-ecosystem

# Codex (plugins-cli)
# Source in ~/plugins/<name>, register in ~/.agents/plugins/marketplace.json,
# enable as <name>@plugins-cli in ~/.codex/config.toml

# Hermes Agent
hermes plugins install Allura-Ecosystem/allura-plugins

# OpenClaw
openclaw plugins install allura-ecosystem:allura-cowork
```

### Update All Runtimes

```bash
# Update plugins across all 4 runtimes (Claude, Codex, Hermes, OpenClaw)
./scripts/plugins-update-all.sh
```

## Model Governance

The [`docs/models.yaml`](docs/models.yaml) registry is the **single source of truth** for agent→model mapping across all runtimes. It covers 47 agents (10 Team RAM + 13 Team Durham + 1 cowork + runtime defaults) across 7 models.

### Design Principles (research-informed)

- **Static registry file** at a well-known location — [arxiv 2508.03095](https://arxiv.org/abs/2508.03095)
- **Centralized management**, not scattered per-agent YAML — [Solace Agent Mesh](https://github.com/solace-ai-solutions/solace-agent-mesh)
- **Per-agent override** > global default — [OpenClaw](https://github.com/Allura-Ecosystem/AionUi)
- **Fallback chains** for resilience — [RouteLLM](https://github.com/lm-sys/RouteLLM)
- **CLASSIC eval framework** (Cost, Latency, Accuracy, Stability, Security, Intelligence) — [Aisera](https://aisera.com)
- **Three-level assessment** (end-to-end, trajectory, component) — AWS/Amazon
- **Canary before promotion** — industry standard
- **Cost-aware routing** — RouteLLM benchmark (~48% cost reduction, Phase 5 future)

### Models Defined

| Model | Provider | Tier | Cost (in/out per 1M) | Runtimes |
|-------|----------|------|----------------------|----------|
| `claude-opus-4-8` | anthropic | ultrabrain | $15 / $75 | claude, opencode, openclaw |
| `claude-sonnet-4` | anthropic | builder | $3 / $15 | claude, opencode, openclaw |
| `claude-haiku-4-5` | anthropic | recon | $0.80 / $4 | claude, opencode, openclaw |
| `ollama-glm-5-2` | ollama | ultrabrain | Free | opencode |
| `ollama-qwen3-coder` | ollama | builder | Free | opencode |
| `ollama-nemotron-3-super` | ollama | recon | Free | opencode |
| `minimax-m3` | minimax | builder | $0.70 / $2.80 | codex |

### Scripts

| Script | Purpose |
|--------|---------|
| `scripts/models-update-all.sh` | Sync agent frontmatter to registry. Runtime-specific aliases. Drift detection. **Dry-run first.** |
| `scripts/models-eval.sh` | CLASSIC eval framework against fixtures. Weekly cadence. 85% pass, 90% ship. |
| `scripts/models-performance.sh` | Aggregate `MODEL_INVOKED` events from Allura Brain. Per-(agent, model, task_class) tracking. |
| `scripts/commands-audit.sh` | Audit orphans, format drift, missing frontmatter, command collisions across plugins. |
| `scripts/plugins-update-all.sh` | Update plugins across all 4 runtimes (Claude, Codex, Hermes, OpenClaw). |

### Eval Fixtures

Located in `evals/fixtures/`. Each fixture defines a task, expected behavior, and scoring rubric for the CLASSIC framework.

Current fixtures (5 of 47 agents):
- `brooks.md` — architecture decision task
- `woz.md` — implementation task
- `scout.md` — recon task
- `qa-reviewer.md` — QA gate task
- `visual-director.md` — visual direction task

> **42 fixtures pending.** See `docs/models.yaml` `agents.*.eval_fixture` for the full list.

### Lifecycle

```
deprecation → canary (7 days on scout/woz) → promotion → rollback
```

Rollback triggers: eval fail, latency regression >20%, cost regression >15%, security gate fail.

## Plugins in this Repo

```
allura-plugins/
├── .claude-plugin/marketplace.json   # Claude marketplace (4 plugins)
├── allura-cowork/                    # Cowork protocol plugin
├── team-durham/                      # Team Durham brand harness
├── team-ram-coding/                  # Team RAM coding plugin
├── team-ram-payload/                 # Payload CMS plugin (Codex-only)
├── plugins/hermes-allura-brain/      # Hermes Agent memory provider
├── docs/
│   ├── models.yaml                   # Model governance registry (source of truth)
│   ├── MARKETPLACE-IDS.md             # Cross-runtime plugin registry
│   ├── BLUEPRINT.md
│   ├── SOLUTION-ARCHITECTURE.md
│   ├── DESIGN-PLUGIN-CATALOG.md
│   ├── SYNC-CONTROL-PLANE.md
│   ├── AGENTS-INVENTORY.md
│   ├── REQUIREMENTS-MATRIX.md
│   ├── RISKS-AND-DECISIONS.md
│   └── DATA-DICTIONARY.md
├── scripts/                          # Update, audit, eval, performance scripts
└── evals/
    ├── fixtures/                     # CLASSIC eval fixtures
    └── results/                      # Eval run results
```

## Documentation

- [Blueprint](docs/BLUEPRINT.md)
- [Solution Architecture](docs/SOLUTION-ARCHITECTURE.md)
- [Catalog Design](docs/DESIGN-PLUGIN-CATALOG.md)
- [Sync Control Plane](docs/SYNC-CONTROL-PLANE.md)
- [Agents Inventory](docs/AGENTS-INVENTORY.md)
- [Requirements Matrix](docs/REQUIREMENTS-MATRIX.md)
- [Risks and Decisions](docs/RISKS-AND-DECISIONS.md)
- [Data Dictionary](docs/DATA-DICTIONARY.md)
- [Model Registry](docs/models.yaml)
- [Marketplace IDs](docs/MARKETPLACE-IDS.md)
- [Progress](PROGRESS.md)

## License

MIT — see [LICENSE](LICENSE).