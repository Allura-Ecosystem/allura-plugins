---
name: payload-debug-first
description: Use when Payload CMS or Next.js/Payload routes, builds, admin screens, hydration, APIs, Docker/dev runtime, or deployments fail; requires evidence before patches.
---

# Payload Debug First

Use this when something is broken, blank, flaky, slow, timing out, failing to build, or failing in Payload admin.

## Debug Order

1. State the symptom in plain language.
2. Reproduce it with the smallest reliable command or browser action.
3. Gather evidence.
   - Server logs.
   - Browser console.
   - Network failures.
   - HTTP status and response body.
   - Build output.
   - Route file and config location.
   - Payload config and generated types.
   - Environment/runtime state.
4. Separate likely layers.
   - Dev server or container.
   - Routing and route groups.
   - Payload config.
   - Collection/global schema.
   - Auth/session.
   - Data, seed, or content state.
   - Frontend hydration.
   - Deployment, DNS, SSL, or edge/runtime behavior.
5. Make the smallest targeted fix.
6. Rerun the failing check and one nearby regression check.
7. Record evidence and remaining risk.

## Rules

- Do not patch before finding the likely cause unless the evidence is already clear.
- Do not treat blank screenshots as proof of UI success or failure by themselves.
- Do not assume stale paths from another repo.
- Do not hide harness instability as app failure.
- Preserve unrelated user changes in a dirty worktree.

## Done Standard

The issue is fixed only when the original symptom no longer reproduces and the verification output is recorded.
