# Public Release Readiness Plan — allura-plugins

**Target:** public GitHub marketplace (`Allura-Ecosystem/allura-plugins`), installable by anyone via
`/plugin marketplace add Allura-Ecosystem/allura-plugins`.

**Shipping set (3 plugins):** `allura-cowork`, `team-durham`, `team-ram-coding`.
**Dropped:** `team-ram-harness` (OpenCode harness, broken source path), `team-ram-payload` (Codex-only, no longer needed).

**Status at audit (2026-07-26):** not releasable. Local `main` == `origin/main` at `aa8f841`.
No credentials found in the repo — all `API_KEY` / `TOKEN` / `PASSWORD` hits are placeholders or env-var names.

---

## 1. Release blockers

These must be closed before the repo goes public.

### B1 — `marketplace.json` points at a directory that does not exist

`.claude-plugin/marketplace.json` declares `team-ram-harness` with
`"source": "../Agent-Harnesses/Allura-TeamRam"`. That path escapes the marketplace root and resolves to
nothing on disk. Any consumer adding the marketplace hits a broken entry.

Fix: delete the `team-ram-harness` object from the `plugins` array, leaving three entries. The harness
itself stays where it is (`Allura-ecosystem/plugins/team-ram/`) as an OpenCode artifact — it is not a
Claude plugin and should not be advertised as one.

### B2 — `team-ram-payload/` is still in the repo

Codex-only package with a `.codex-plugin/plugin.json` and no Claude manifest. Not referenced by
`marketplace.json`. Confirmed no longer needed. Delete the directory.

### B3 — No LICENSE file exists

`README.md` states "MIT — see [LICENSE](LICENSE)" but there is no `LICENSE` file anywhere in the repo.
On a public repo with no license, default copyright applies and nobody may legally reuse the code —
which defeats the point of publishing.

Fix: add a root `LICENSE` (MIT, copyright Allura Ecosystem). Add `"license": "MIT"` to
`allura-cowork/.claude-plugin/plugin.json` and `team-ram-coding/.claude-plugin/plugin.json`; both
currently omit the field. `team-durham` already declares it.

### B4 — Personal environment data is committed and already pushed

`evidence/inventory/20260611T110512Z/raw/` contains `claude-plugin-list.json`, `codex-plugin-list.json`,
`candidate-packages.json`, and `manifest-paths.txt`. These record your machine's absolute install paths
(`/home/ronin704/.claude/plugins/cache/...`), your full installed-plugin and marketplace inventory,
and local cache errors. Not credentials, but it is a detailed map of your workstation.

`.gitignore` has `evidence/inventory/raw/`, which does not match the timestamped path
`evidence/inventory/<TS>/raw/` — so these files are tracked, committed, and on origin.

Fix: correct the ignore pattern to `evidence/inventory/**/raw/`, remove the files from the working tree,
**and scrub them from git history** (`git filter-repo` or a fresh squashed history) before flipping the
repo to public. Force-push after scrubbing.

### B5 — Hardcoded personal paths inside shipped plugin content

Nine files ship absolute paths from your machine. Several are stale even locally — `multi-search`
instructs agents to grep `/home/ronin704/Projects/allura memory/`, which no longer exists (the repo
lives at `Allura-ecosystem/allura-memory`). A public installer gets skills that point at nothing.

| File | Problem |
|---|---|
| `team-ram-coding/skills/multi-search/SKILL.md` | 7 references to `/home/ronin704/Projects/allura memory/` (stale path) |
| `team-ram-coding/skills/allura-memory-skill/SKILL.md` | MCP `args` point at `/home/ronin704/Projects/allura memory/src/mcp/...` |
| `team-ram-coding/skills/mcp-docker/SKILL.md` | `/home/ronin704/dev/projects/memory` in examples |
| `team-durham/skills/mcp-docker/SKILL.md` | same |
| `team-durham/skills/mcp-libre/SKILL.md` | `/home/ronin704/tools/mcp-libre/libreoffice_mcp_server.py` |
| `team-durham/skills/fal-ideogram-executor/reference/round4-execution-guide.md` | `cd /home/ronin704/Projects/Brand maker` |
| `team-durham/source/opencode/opencode.json` | `.nvm` node binary, `/media/ronin704/Games/Projects/open-design/...`, three brand-maker skill dirs |
| `team-durham/source/opencode/scripts/validate-team-durham-config.mjs` | same brand-maker paths |
| `allura-cowork/hooks/hooks.json` | fallback `/home/ronin704/plugins/allura-cowork` |

Fix: replace with `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PROJECT_DIR}`, or generic placeholders
(`/path/to/your/project`). Where a skill genuinely needs a user-specific location, make it a documented
env var with a stated default, not a baked-in string.

### B6 — `team-durham/source/opencode/` is authoring residue

An OpenCode config tree and validator script carried inside the distributed Claude plugin. It is the
worst offender for leaked paths (B5) and serves no purpose for an installer. Delete the `source/`
directory from the plugin.

### B7 — Hooks assume an interpreter is on PATH and fail loudly when it is not

`allura-cowork/hooks/hooks.json` runs `hooks/cowork-context.py` on every `UserPromptSubmit` with no
guard that `python3` exists. This is not theoretical: during this audit session a *different* installed
plugin's `SessionEnd` hook failed repeatedly with `/bin/sh: 1: node: not found`, printing an error into
the transcript on every tool call.

Fix: wrap hook commands so a missing interpreter is a silent no-op rather than a visible error, and
document the runtime requirement in the plugin README. Remove the personal fallback path.

---

## 2. Should fix before public

### S1 — CI validates nothing

`.github/workflows/ci.yml` `validate-plugins` iterates `plugins/*/`. The catalog's plugins live at the
repo **root** (`team-durham/`, `team-ram-coding/`, `allura-cowork/`), so the loop matches zero
directories, reports "Checked 0 plugin directories", and passes. It also looks for `$d/plugin.json`
rather than `$d/.claude-plugin/plugin.json`. Nothing anywhere validates `marketplace.json` — which is
exactly why B1 shipped undetected.

Rewrite the workflow to assert:

1. `marketplace.json` parses, and every `source` resolves to a directory **inside** the repo.
2. Every declared plugin has `.claude-plugin/plugin.json` that parses.
3. Every `agents[]` and `commands[]` path in each `plugin.json` exists on disk.
4. Every `skills/*/SKILL.md` has valid frontmatter with `name` and `description`.
5. No `/home/` or `/media/` string appears in any shipped plugin directory.
6. Versions in `marketplace.json` match the corresponding `plugin.json`.

Check 5 alone would have caught nine files. Check 1 would have caught the release blocker.

### S2 — Missing `team-ram-coding/README.md`

`allura-cowork` and `team-durham` both have one; `team-ram-coding` does not. Every publicly listed
plugin needs a README covering what it does, what it requires, and how to use it.

### S3 — Version bumps (required for consumers to receive the update)

Desktop and CLI clients key off the version. Editing content without bumping means nobody re-fetches.

| Plugin | Current | Proposed |
|---|---|---|
| `allura-cowork` | 0.1.0 | 0.2.0 |
| `team-durham` | 0.1.0 | 0.2.0 |
| `team-ram-coding` | `0.1.0+codex.20260530050504` | 0.2.0 |

Drop the `+codex.<timestamp>` build metadata — it is local provenance, meaningless to a public
consumer, and makes the version hard to read.

### S4 — Orphan files that silently never load

- `team-durham/agents/scout-recon.md` — not listed in `plugin.json`'s `agents[]`, so it never loads.
- `team-ram-coding/commands/openagents/check-context-deps.md` — nested a level deeper than the command
  loader scans, so it never registers.

Either wire them into the manifests or delete them. Shipping dead files invites bug reports.

### S5 — Undeclared third-party dependencies

Skills across both plugins assume Allura Brain on `localhost:5888`, Docker MCP toolkit, fal.ai, Figma,
Notion, and LibreOffice MCP. A public installer with none of these gets skills that fail at the point
of use with no explanation.

Fix: add a **Requires** section to each affected `SKILL.md` and to each plugin README, and make the
skills detect a missing dependency and say so rather than erroring.

### S6 — Public-facing docs contradict the shipped state

- `README.md` advertises 4 plugins; after B1/B2 there are 3.
- `README.md` documents `plugins/hermes-allura-brain/` in the repo tree; that directory does not exist.
- `README.md` links `LICENSE`, which does not exist (B3).
- `PROGRESS.md` shows Phases 2–7 unchecked, including "Phase 4: Migrate and verify Claude" — a public
  repo whose own tracker says the Claude migration is unverified undercuts the entire pitch.

Fix: rewrite `README.md` for the 3-plugin reality; replace `PROGRESS.md` with a forward-looking public
roadmap and move the internal phase tracker out of the repo (or into a private issue).

---

## 3. Nice to have

- `CONTRIBUTING.md`, `SECURITY.md`, and issue templates — expected furniture on a public org repo.
- Tag `v0.2.0` on release so consumers can pin a known-good marketplace revision.
- `docs/models.yaml` ships your model routing and cost table. Fine to publish, but the README claims
  "5 of 47 eval fixtures" — either build more or soften the claim.
- Consider whether `evals/results/` (dated run output referencing your paths) belongs in a public repo
  at all; same category as B4, lower severity.

---

## 4. Suggested sequencing

| Step | Work | Gate |
|---|---|---|
| 1 | B1, B2 — marketplace.json trimmed to 3, `team-ram-payload/` deleted | Marketplace resolves cleanly |
| 2 | B5, B6 — path sweep, `source/` deleted | `grep -r "/home/\|/media/"` over the 3 plugin dirs returns nothing |
| 3 | B7, S5 — hook hardening, dependency declaration | Fresh install on a clean machine produces no errors |
| 4 | B3, S2, S6 — LICENSE, missing README, doc rewrite | Docs match shipped reality |
| 5 | S1 — CI rewrite | CI fails on a deliberately broken `source` path (prove it works) |
| 6 | B4 — history scrub, force-push | `git log -p` over history shows no `evidence/**/raw/` |
| 7 | S3, S4 — version bumps, orphan cleanup, tag `v0.2.0` | — |
| 8 | Flip repo to public | Install from a second machine/account end to end |

Step 6 is deliberately late: do the history scrub **last**, after all content edits are committed, so you
rewrite history exactly once.

---

## 5. Release gate

Do not make the repo public until every line is true.

- [ ] `marketplace.json` lists exactly 3 plugins and every `source` resolves inside the repo
- [ ] `team-ram-payload/` and `team-durham/source/` are deleted
- [ ] No `/home/` or `/media/` string in `allura-cowork/`, `team-durham/`, `team-ram-coding/`
- [ ] Root `LICENSE` exists; all 3 `plugin.json` files declare `"license"`
- [ ] All 3 plugins have a README stating purpose, requirements, and usage
- [ ] Hooks no-op safely when their interpreter is absent
- [ ] Every agent and command path in every `plugin.json` exists on disk
- [ ] CI fails on a deliberately broken `source` path (verified, not assumed)
- [ ] `evidence/**/raw/` is gone from the working tree **and** from git history
- [ ] Versions bumped to 0.2.0 and tagged
- [ ] `README.md` and `PROGRESS.md` describe the 3-plugin public reality
- [ ] Clean-machine install test passed from the public URL

---

## 6. Out of scope

`team-ram-harness` (`Allura-ecosystem/plugins/team-ram/`, v0.4.2) stays an OpenCode artifact and is not
published here. If it should ship publicly later it needs its own effort: vendoring into this repo,
restructuring `.opencode/command/` into a Claude-compatible layout, and the same path/secret sweep.
