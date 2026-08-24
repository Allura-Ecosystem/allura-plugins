<p align="center">
  <img src="allura/assets/logo.png" alt="Allura" width="180" />
</p>

<h1 align="center">Allura Plugins</h1>

<p align="center">
  <strong>Governed agent teams for coordination, brand production, and software delivery.</strong><br/>
   One organization-owned catalog for Claude, Codex, and Hermes plugin packages, model policy, and validation tooling.
</p>

<p align="center">
  <a href="#catalog">Catalog</a> ·
  <a href="#installation">Installation</a> ·
  <a href="#how-the-plugins-fit-together">Architecture</a> ·
  <a href="#model-governance">Model governance</a> ·
  <a href="#validation">Validation</a> ·
  <a href="#repository-map">Repository map</a>
</p>

---

<p align="center">
  <a href="docs/images/infographic-plugin-system-v3.png"><img src="docs/images/infographic-plugin-system-v3.png" alt="Allura plugin system with Allura Cowork, Team Durham, and Team RAM Coding above a single Allura Memory governance foundation, with Allura Brain identified as its functional alias and Claude and Codex shown as distinct execution surfaces" width="900" /></a><br/>
  <sub><a href="docs/images/infographic-plugin-system-v3.png">Open the full-size infographic</a></sub>
</p>

## What this repository owns

`allura-plugins` is the canonical source and governance repository for the Allura plugin layer. It has three jobs:

1. **Plugin catalog** — maintain Allura workflow packages and their Claude/Codex manifest surfaces.
2. **Model governance** — map agents to primary models, runtime aliases, and fallback chains in one registry.
3. **Release evidence** — provide checks and evidence paths for manifests, commands, examples, hooks, evals, and runtime-specific updates before a plugin is treated as ready.

Plugins add skills, commands, and operating roles. They do not replace Allura Brain or bypass its memory governance.

## Catalog

The Claude marketplace contains three versioned packages, and the repository also ships one Hermes-native provider. Counts below are source definitions measured from the current repository tree; they are not counts of agents currently installed, loaded, or running in any runtime.

| Plugin | Release metadata | Agent definitions | Command definitions | Skill definitions | Purpose |
|---|:---:|---:|---:|---:|---|
| [Allura Cowork](allura-cowork/README.md) | 0.2.0 | 1 | 4 | 1 | Coordinate Claude and Codex with hydration, honest attribution, evidence, handoff, and closeout |
| [Team Durham](team-durham/README.md) | 0.2.0 | 13* | 21 | 77 | Run brand strategy, naming, visual direction, production, accessibility, and QA |
| [Team RAM Coding](team-ram-coding/README.md) | 0.2.0 | 11 | 35 | 12 | Run Brooks-led architecture, recon, implementation, review, and validation |
| [Hermes Allura Brain](plugins/hermes-allura-brain/README.md) | 0.2.0 | — | 1 | — | Hermes-native governed recall and outcome persistence provider |

Release metadata is `0.2.0` in the Claude marketplace, each Claude/Codex
`plugin.json`, and each portable package's `package.json`.

\* Team Durham has 13 agent-definition files registered in its Claude manifest. Its package README names 12 canonical roles; the additional definition is `openagent`, a generic fallback. Until the package documentation resolves whether that fallback belongs to the canonical roster, describe Durham as **13 definitions / 12 named canonical roles**, not as 13 running agents.

Team RAM Coding has 35 command-definition files, and both current runtime
manifests and its package README register all 35.

Hermes Allura Brain is a Hermes-native provider declared by `plugins/hermes-allura-brain/plugin.yaml`; it is intentionally not listed in the Claude marketplace because it does not implement the Claude/Codex package-manifest contract.

The `allura/` directory is a local Codex README asset and guidance pack. It is not listed as a public Claude marketplace package and still contains manifest placeholders; treat it as internal support material until those fields are resolved.

### Allura Cowork

Use Allura Cowork when a task crosses Claude and Codex or needs a durable runtime handoff.

```text
Hydrate project + Brain
    ↓
Name the active runtime
    ↓
Route work and define evidence
    ↓
Create/validate handoff
    ↓
Close with outcome + remaining risk
```

Its core promise is runtime honesty: adopting a named perspective is not the same as executing a real second runtime or subagent.

### Team Durham

Team Durham is the brand-production system. Its canonical route is:

```text
Brief → strategy → positioning → verbal identity
      → visual direction → production → accessibility → QA
```

The agent roster covers orchestration, strategy, copy, visual direction, brand systems, evidence, QA, and operational trust. Optional integrations support Figma, Penpot, image generation, Notion, and document production.

### Team RAM Coding

Team RAM Coding is the governed software-delivery system. Brooks owns conceptual integrity and routing; Scout loads context; Woz implements; Pike and Fowler review interfaces and change safety.

```text
Brooks → Scout → Allura Brain → required skills
       → build/review → validate → log
```

The plugin includes task management, code review, multi-source research, MCP orchestration, security policy, secret-handling, and multi-agent dispatch skills.

## How the plugins fit together

| Need | Lead plugin | Supporting plugin |
|---|---|---|
| Cross-runtime collaboration | Allura Cowork | Team RAM Coding or Team Durham executes the domain work |
| Product or engineering work | Team RAM Coding | Cowork handles runtime handoff |
| Brand strategy and production | Team Durham | Cowork handles runtime handoff |
| Persistent project context | Allura Brain connection | Every plugin follows the same scoped memory rules |

The plugins are composable but keep distinct ownership:

- **Cowork coordinates.**
- **Durham creates and protects brand intent.**
- **Team RAM Coding builds and validates software.**
- **Allura Brain remembers and governs.**
- **Hermes Allura Brain connects Hermes to governed recall and outcome persistence.**

## Shared operating contract

All catalog plugins inherit the same Allura expectations:

- search relevant project context before substantive work;
- use `group_id: allura-system` unless the project declares another valid `allura-*` tenant;
- treat raw episodic traces as evidence, not canonical truth;
- identify the actual runtime and never claim an agent or tool executed when it did not;
- preserve approval boundaries for secrets, production, scheduling, promotion, and destructive actions;
- validate the result before calling work done;
- write a factual outcome receipt after substantive work when Allura Brain is available.

## Installation

### Claude marketplace

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install allura-cowork@allura-ecosystem
/plugin install team-durham@allura-ecosystem
/plugin install team-ram-coding@allura-ecosystem
```

The Claude catalog is defined in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json). Each package also owns its own `.claude-plugin/plugin.json`. Hermes uses its native provider manifest instead; follow [its package README](plugins/hermes-allura-brain/README.md).

### Codex

Each catalog package contains a `.codex-plugin/plugin.json` manifest. The repository does not itself prove that a given Codex build accepts, installs, or loads every declared surface. For a compatible Codex environment, clone this repository into your plugin source location, register the package through that environment's supported local-plugin flow, and verify it appears after restart.

The root [`.agents/plugins/marketplace.json`](.agents/plugins/marketplace.json) is currently an empty index shell (`plugins: []`), not evidence that these packages are registered in Codex.

### Requirements

| Requirement | Applies to |
|---|---|
| A compatible Claude Code or Codex plugin environment | Targeted by the package manifests; verify loading in the actual runtime |
| Allura Brain MCP connection | Expected for governed hydration and outcome logging |
| Python 3 | Allura Cowork hooks and validation scripts |
| Docker | Optional MCP Docker, secret, and infrastructure workflows |
| Figma, Penpot, Notion, fal.ai, LibreOffice | Optional Team Durham integrations only |

Missing optional integrations should degrade visibly and leave the core plugin loadable.

## Updating runtimes

Preview changes before applying them:

```bash
bash scripts/plugins-update-all.sh --dry-run
```

Run the helper's non-dry-run update attempts on detected surfaces:

```bash
bash scripts/plugins-update-all.sh
```

Target one plugin or runtime:

```bash
bash scripts/plugins-update-all.sh team-durham
bash scripts/plugins-update-all.sh --runtime codex
```

The helper scans Claude, Codex, Hermes, and OpenClaw-shaped surfaces, but behavior is asymmetric: it can sync the Claude marketplace and operate on detected Claude/Hermes/OpenClaw installations, while its Codex path currently inventories local manifest versions. It is not proof that all four runtimes support or have loaded these plugins; verify each target runtime separately.

## Model governance

[`docs/models.yaml`](docs/models.yaml) is the source of truth for agent-to-model policy. It records:

- model provider and capability tier;
- context window, cost metadata, and latency profile;
- runtime availability and aliases;
- each agent's primary model and fallback chain;
- canary, evaluation, deprecation, and rollback policy.

The registry contains model-policy and alias entries for multiple runtime names. Those entries describe intended routing where a runtime integration exists; they do not establish installation, feature parity, or successful execution on Claude, OpenCode, Codex, Hermes, or OpenClaw.

### Model workflow

```text
Edit models.yaml
    ↓
Dry-run frontmatter sync
    ↓
Run evaluation fixtures
    ↓
Canary the candidate model
    ↓
Promote or roll back with evidence
```

Commands:

```bash
bash scripts/models-update-all.sh --dry-run
bash scripts/models-eval.sh
bash scripts/models-performance.sh
```

Do not hand-edit scattered agent model fields and then treat them as policy. Update the registry first, inspect the dry run, and sync deliberately.

## Validation

### Catalog checks

| Command | What it checks |
|---|---|
| `bash scripts/commands-audit.sh` | Orphan commands, manifest format, frontmatter, and cross-plugin collisions |
| `bash scripts/models-update-all.sh --dry-run` | Model assignment drift without mutation |
| `bash scripts/models-eval.sh` | CLASSIC evaluation fixtures |
| `bash scripts/plugins-update-all.sh --dry-run` | Cross-runtime version/update impact |

These are local audit helpers and are not all run by the current GitHub Actions workflow.

### Current CI coverage

The current [`.github/workflows/ci.yml`](.github/workflows/ci.yml) checks:

- the Claude marketplace parses and each listed source resolves inside the repository;
- the Hermes-native `plugins/hermes-allura-brain/plugin.yaml` declares a valid `allura-brain` provider identity, version, and description;
- Claude marketplace versions match the corresponding Claude `plugin.json` versions;
- explicitly listed Claude agent paths and all declared Claude command paths exist; list-valued agent manifests and top-level command directories have no on-disk orphans, and nested command definitions are rejected;
- shipped marketplace plugin directories do not contain the workflow's machine-path patterns or prohibited embedded runtime-config directories;
- every repository `plugin.json` parses as JSON;
- the root README and LICENSE exist; and
- a small set of credential patterns is absent from selected text-file extensions.

CI does **not** currently validate `package.json` version parity, Codex manifest path/content parity beyond JSON parsing, command frontmatter, skill metadata, model-registry drift, package evals, Cowork schemas/examples/hooks, external integrations, native runtime installation/loading, or cross-runtime behavioral parity. The workflow name's “5 invariants” refers only to the five structural checks in its Claude-marketplace validation script.

### Package checks

Allura Cowork:

```bash
python3 allura-cowork/scripts/validate_plugin.py allura-cowork
python3 allura-cowork/scripts/run_evals.py allura-cowork
```

Team Durham's validation skills and Team RAM Coding's review gates are documented in their package READMEs and skill folders. These are available validation definitions, not evidence that CI ran them. A manifest parsing successfully is necessary, but it is not sufficient evidence that every command, hook, dependency, runtime, or external integration works.

### Definition of ready

A plugin release should have the following evidence before it is described as runtime-ready. The present CI workflow does not enforce every item:

1. valid Claude and Codex manifests;
2. registered commands with descriptions;
3. complete skill metadata;
4. no unexplained command collisions;
5. passing package-specific tests/evals;
6. reviewed model-registry changes;
7. documented optional dependencies and degraded behavior;
8. version parity between package and marketplace metadata;
9. an evidence-backed release note.

## Plugin anatomy

```text
<plugin>/
├── .claude-plugin/plugin.json   Claude package manifest
├── .codex-plugin/plugin.json    Codex package manifest
├── agents/                      specialist role definitions
├── commands/                    user-invoked workflows
├── skills/                      reusable operating instructions
├── hooks/                       optional lifecycle hooks
├── scripts/                     validation and package tooling
├── evals/                       behavior fixtures
└── README.md                    package-specific contract
```

Not every package needs every directory. Keep the manifest surface as small as the product requires.

## Repository map

```text
allura-plugins/
├── .claude-plugin/marketplace.json   Claude marketplace catalog
├── .agents/plugins/marketplace.json  Codex marketplace index shell
├── allura-cowork/                    coordination and handoff plugin
├── team-durham/                      brand-production plugin
├── team-ram-coding/                  engineering plugin
├── plugins/hermes-allura-brain/       Hermes-native Allura Brain provider
├── _bmad/bmm/                         catalog-local epics and stories
├── allura/                           internal README asset/guidance pack
├── docs/models.yaml                  canonical model registry
├── docs/images/                      README brand assets
├── scripts/                          update, audit, and eval tooling
└── evals/fixtures/                   shared evaluation fixtures
```

## Contributing

- Make changes inside the owning plugin; avoid cross-package coupling without a clear shared contract.
- Update both Claude and Codex manifests when the public surface changes.
- Add commands explicitly rather than relying on broad globs.
- Keep secrets and credentials out of manifests, prompts, examples, and test output.
- Preserve user changes in dirty worktrees.
- Run the narrowest relevant validation first, then the catalog checks.
- Document external dependencies as optional unless the plugin cannot function without them.

## Brand system

The plugin catalog uses the canonical Allura visual language:

- Allura Blue `#0D47A1` — intelligence and coordination
- Allura Orange `#FF4D1F` — clarity and creative decision
- Allura Green `#14BA4B` — connection and delivery
- Allura Ink `#0F1720` — technical structure
- Allura Cream `#F7F3EE` — readable editorial space
- Aeonik — display, heading, and body typography
- IBM Plex Mono — code and technical identifiers

## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <strong>Coordinate clearly. Create deliberately. Build with evidence.</strong>
</p>
