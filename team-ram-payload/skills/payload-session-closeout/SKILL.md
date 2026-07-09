---
name: payload-session-closeout
description: Use before ending a governed Payload work session to summarize changes, validate evidence, record blockers, and log Allura outcomes when memory tools are available.
---

# Payload Session Closeout

Use this before handing back important Payload work.

## Closeout Checklist

1. Review the changed files.
   - `git status --short`.
   - `git diff --stat`.
   - Targeted diffs for files you touched.
2. Confirm docs and code agree.
   - Schema/config changes have matching docs.
   - Route/content changes have matching acceptance evidence.
   - Decisions and risks are recorded when durable.
3. Run verification.
   - Use the smallest meaningful checks for the changed path.
   - Prefer repo scripts.
   - For Payload schema/config: generate types/import map when available.
   - For routes: smoke or browser checks.
   - For docs-only changes: link/path and format checks where practical.
4. Separate evidence from memory.
   - Allura memory is context and audit.
   - Tests, build, smoke, source docs, health checks, MCP receipts, screenshots, and user approval are proof.
5. Log outcome when memory tools are available.
   - Explicit `group_id`.
   - What changed.
   - Why it changed.
   - Verification evidence.
   - Open blockers or risks.
   - No secrets or private data.

## Final Reply Shape

Keep it short and operational:

- What changed.
- Where it changed.
- Verification run and result.
- Remaining blockers or risks.
- Memory log status if relevant.
