---
name: payload-project-hydration
description: Use at the start of Payload CMS or Next.js/Payload sessions to map project authority, repo shape, runtime, route roots, memory context, and blockers before editing.
---

# Payload Project Hydration

Use this before substantive work in a Payload website or app repo.

## Workflow

1. Confirm workspace identity.
   - `pwd`
   - `git rev-parse --show-toplevel`
   - `git status --short --branch`
2. Read local authority in order.
   - Nearest `AGENTS.md`.
   - Repo README and project docs.
   - `.opencode/`, `.agents/`, `.claude/`, or equivalent local agent files.
   - Package scripts and runtime docs.
   - Payload config, Next config, Docker/dev files, deployment files.
3. Find the app shape.
   - `package.json`
   - `src/payload.config.*` or `payload.config.*`
   - `src/collections/**`, `src/globals/**`, `src/blocks/**`
   - `src/app`, `app`, `pages`, `public`
   - route groups such as `(frontend)` or `(payload)`
4. Check Allura memory when tools are available.
   - Use explicit `group_id`.
   - Default to `allura-system`.
   - Follow repo-declared namespace if present.
   - Search for project name, blockers, architecture decisions, session ends, route/runtime lessons, and active branch context.
5. Produce a short hydration receipt.
   - Project/client.
   - Branch and dirty state.
   - Source-of-truth docs.
   - Payload config location.
   - Route root.
   - Runtime command or container path.
   - Known smoke/test commands.
   - Blockers or unknowns.
   - Next action.

## Rules

- Do not assume route roots from memory or another project.
- Do not claim a subagent, memory search, test, browser check, or runtime check happened unless it actually ran.
- If local docs, memory, user request, and tool output conflict, pause and name the conflict.
- Keep secrets out of summaries and memory.

## Optional Probe

From a repo root, run the read-only helper when useful:

```bash
/home/ronin704/plugins/team-ram-payload/scripts/probe-payload-project.sh
```
