# Allura Harness Sync — Drift Detection & Repair

## The Problem

The Allura ecosystem has **5 plugin directories** under `~/plugins/`, and each team's harness is duplicated across multiple project copies. Over time, these copies **drift**:

- **598 commits** landed with secrets baked into governance docs — the same docs copied across 4+ projects.
- **4 copies** of governance documentation exist, none identical, each with its own drift.
- Agent personas (`agents/*.md`) and slash commands (`commands/*.md`) diverge silently. A fix to `scout.md` in the canonical source never propagates to project copies.
- The `.codex-plugin/plugin.json` manifest gets out of sync, causing plugin discovery to fail in some projects but not others.

Nobody notices until something breaks. By then, you're diffing 4 directories by hand.

## The Solution

**Harness Sync** treats the harness as two layers:

| Layer  | Files                                     | Synced?  |
|--------|-------------------------------------------|----------|
| CORE   | `agents/*.md`, `commands/**/*.md`, `.codex-plugin/plugin.json` | YES — must be identical everywhere |
| OVERLAY | `skills/**`, `config/**`, `scripts/**`, `hooks/**`, `assets/**`, `.claude-plugin/**`, `README.md` | NO — per-project customization |

The canonical source for each team is:

| Team   | Canonical Source           | Project Copies (share core)              |
|--------|---------------------------|------------------------------------------|
| RAM    | `team-ram-coding/`        | `team-ram-payload/`, `allura-cowork/`, `allura/` |
| Durham | `team-durham/`            | *(none yet — add as they appear)*         |

The script (`harness-sync.sh`) compares each project copy's core files against the canonical source and reports drift. It can also repair drift by copying core files from canonical to projects.

## Quick Start

### Check for drift (all teams, all projects)

```bash
~/plugins/harness-sync.sh --check
```

Output:
```
╔══════════════════════════════════════════════════════════════╗
║         Allura Harness Sync — Drift Detection & Repair       ║
╚══════════════════════════════════════════════════════════════╝

Core files:    agents/*.md, commands/**/*.md, .codex-plugin/plugin.json
Overlay files: skills/**, config/**, scripts/**, hooks/**, assets/**, etc.
Mode:          check
Team:          all
Project:       all

=== Team: RAM | Project: team-ram-payload ===
...
  *** NO DRIFT ***

=== Team: RAM | Project: allura-cowork ===
...
  *** CORE DRIFT FOUND ***

  NO DRIFT — All core harness files are in sync.
```

Exit code: `0` if no drift, `1` if drift found.

### Check one team

```bash
~/plugins/harness-sync.sh --check --team ram
```

### Check one specific project

```bash
~/plugins/harness-sync.sh --check --team ram --project allura-cowork
```

### Sync (repair drift)

```bash
# Sync all teams, all projects
~/plugins/harness-sync.sh --sync

# Sync only RAM
~/plugins/harness-sync.sh --sync --team ram

# Sync one project
~/plugins/harness-sync.sh --sync --team ram --project allura-cowork
```

Sync copies core files from the canonical source to each project. Overlay files are never touched.

## CI Integration

The `--check` mode exits non-zero when drift is found, making it suitable for CI:

```bash
# In CI pipeline:
~/plugins/harness-sync.sh --check || {
    echo "Harness drift detected — run harness-sync.sh --sync to repair"
    exit 1
}
```

```yaml
# GitHub Actions example
- name: Check harness drift
  run: ~/plugins/harness-sync.sh --check
```

## File Classification

### Core Files (synced)

These files define the shared harness behavior and MUST be identical across all project copies:

| Pattern                        | Description                          |
|-------------------------------|--------------------------------------|
| `agents/*.md`                 | Agent persona definitions            |
| `commands/*.md`               | Slash command definitions            |
| `commands/*/*.md`             | Nested commands (e.g., `openagents/`) |
| `.codex-plugin/plugin.json`   | Plugin manifest (Codex discovery)     |

### Overlay Files (per-project, NOT synced)

These files are project-specific and are never touched by the sync mechanism:

| Pattern              | Description                              |
|---------------------|------------------------------------------|
| `skills/**`          | Per-project skill packs                  |
| `config/**`          | Per-project configuration                |
| `scripts/**`         | Per-project scripts                      |
| `hooks/**`           | Per-project hooks                        |
| `assets/**`          | Per-project assets (images, logos)       |
| `.claude-plugin/**`  | Claude-specific manifest                 |
| `README.md`          | Per-project readme                       |

## Drift Report Format

The script outputs a table for each project comparison:

```
FILE                                          STATUS     CANON    PROJ     DETAILS
─────────────────────────────────────────────────────────────────────────────────────
.codex-plugin/plugin.json                     OK         842      842      identical
agents/scout.md                               DRIFT      12453    11900    size differs (12453 vs 11900 bytes)
commands/orchestrate.md                       MISSING    3100     -        file not found in project
agents/cowork-orchestrator.md                 EXTRA      -        5600     project-only (overlay — not drift)
```

| Status   | Meaning                                                       |
|----------|---------------------------------------------------------------|
| OK       | File is identical in canonical and project                   |
| DRIFT    | File exists in both but content differs                      |
| MISSING  | File exists in canonical but not in project                  |
| EXTRA    | File exists only in project (not in canonical) — not drift   |
| SYNCED   | (sync mode) File was overwritten from canonical              |
| CREATED  | (sync mode) File was copied from canonical (didn't exist)    |

## Adding New Projects

When a new project plugin is created that shares a team's core harness:

1. Create the plugin directory under `~/plugins/`
2. Edit `harness-sync.sh` and add the project name to the appropriate `RAM_PROJECTS` or `DURHAM_PROJECTS` array
3. Run `harness-sync.sh --sync --team <team> --project <new-project>` to seed core files
4. Verify with `harness-sync.sh --check --team <team> --project <new-project>`

## Why This Matters

1. **Secret leakage**: 598 commits with secrets in governance docs were only caught because someone happened to diff two copies. With drift detection, this is caught at CI time.

2. **Governance consistency**: When `scout.md` agent persona changes in the canonical source, it should change everywhere. Without sync, 3 out of 4 projects still run the old persona.

3. **Plugin discovery reliability**: `.codex-plugin/plugin.json` drift causes plugin discovery to silently fail in some projects. Sync ensures the manifest is always current.

4. **Developer onboarding**: New team members don't need to know which copy is "the real one." The canonical source is authoritative, and the sync mechanism enforces it.

5. **Audit trail**: The drift report shows exactly which files diverged and by how much, making it easy to review changes before syncing.

## Script Location

```
~/plugins/harness-sync.sh
```

Run `~/plugins/harness-sync.sh --help` for full usage.