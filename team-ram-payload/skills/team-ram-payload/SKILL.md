---
name: team-ram-payload
description: Use when a Payload CMS or Next.js/Payload project asks for Team RAM routing, Allura governance, or a start-to-finish governed implementation loop.
---

# Team RAM Payload

Use this as the top-level operating loop for Payload CMS projects that explicitly invoke Team RAM or install this plugin for the session.

## Boundary

Team RAM is opt-in for a project. Do not say Team RAM is global. If the repo declares a local agent system, use that local source of truth. If the repo does not declare Team RAM but the user invokes this plugin, say Codex is applying the Team RAM Payload playbook.

Allura is the memory and governance layer. Allura context is helpful evidence, not proof of done. Done still needs tests, builds, route checks, source documents, MCP receipts, health checks, or user approval.

## Default Loop

1. Hydrate project context.
   - Read nearest `AGENTS.md`.
   - Inspect `.opencode/`, `.agents/`, `.claude/`, README, docs, `package.json`, Payload config, Next config, route tree, Docker/runtime files, and open blocker docs.
   - Check branch and dirty state.
2. Search Allura when tools are available.
   - Use an explicit `group_id`.
   - Default to `allura-system`.
   - If the repo declares another namespace, use the repo namespace.
   - Never claim memory was searched or written unless the tool call succeeded.
3. Route the work.
   - Jobs: intent, scope, acceptance criteria.
   - Scout: read-only repo discovery.
   - Brooks: structure, architecture, operating plan.
   - Woz: implementation.
   - Knuth: schema, data model, generated types.
   - Pike: interface/API simplicity.
   - Fowler: refactor safety and incremental change.
   - Bellard: deep diagnostics.
   - Carmack: performance and rendering latency.
   - Hightower: runtime, deployment, environment, one-command operation.
4. Apply the right skill.
   - `payload-project-hydration` for session start.
   - `payload-governed-development` for schema, block, route, API, seed, auth, or rendering changes.
   - `payload-debug-first` for failures, timeouts, blank screens, bad admin behavior, or route errors.
   - `payload-route-smoke-harness` for browser/route proof.
   - `payload-session-closeout` before completion.
5. Build or review with evidence.
   - Use the smallest meaningful verification that covers the changed path.
   - Do not call work ready until evidence exists.
6. Log the outcome when memory tools are available.
   - Include what changed, why, validation evidence, and open blockers.
   - Never store secrets, tokens, donor PII, CMS credentials, database URLs, or private user data.

## Payload Defaults

- Prefer Payload 3 typed config patterns.
- Regenerate `payload-types.ts` and import maps after schema or admin config changes when scripts exist.
- Keep media alt text meaningful unless the image is explicitly decorative.
- Treat collections as URL-bearing content types; use arrays or blocks for content that only lives inside one page or component.
- Keep access control restrictive until documented.
- Update docs alongside schema, route, API, or business-rule changes when the repo has docs-first governance.

## Lessons To Carry Forward

- Never assume route roots from another repo.
- Clear stale smoke output before rerunning route proof.
- XML/TXT assets are often better as request probes than full browser-render checks.
- Placeholder evidence is not validation.
- Harness instability is a blocker to diagnose, not an app bug to hide.
- Blank screenshots alone are not authoritative proof.
- Allura memory is a gate and audit trail, not a task tracker and not completion proof.

## Completion Receipt

End with:

- Current status.
- Changed files or no-change result.
- Verification commands and results.
- Allura memory status, if tools were available.
- Remaining blockers or risks.
