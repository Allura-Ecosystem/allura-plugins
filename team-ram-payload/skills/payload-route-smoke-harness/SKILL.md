---
name: payload-route-smoke-harness
description: Use to design, run, or review route and browser smoke checks for Payload/Next.js projects, including local Docker/dev servers, static routes, dynamic routes, admin, sitemap, robots, and evidence folders.
---

# Payload Route Smoke Harness

Use this for route validation, browser QA, and launch smoke evidence in Payload/Next.js projects.

## Preflight

1. Identify the real runtime path.
   - Local dev command.
   - Docker compose file and exposed port.
   - Production preview URL.
   - Required env file or missing service.
2. Identify the real route root.
   - `src/app`
   - `app`
   - `pages`
   - route groups such as `(frontend)` and `(payload)`
3. Clear or isolate stale smoke output before rerunning checks.
4. Start with HTML user routes before expanding to feeds, XML, TXT, or admin.

## Route Check Shape

Capture enough evidence to prove the user path:

- URL.
- HTTP status.
- Final URL after redirect.
- Title.
- H1 or main landmark.
- Critical content selectors.
- Console errors.
- Page errors.
- Network failures.
- Accessibility or overflow signals when relevant.
- Screenshot only when it is readable and tied to source/browser evidence.

## XML/TXT Asset Rule

Use request probes for assets such as:

- `/robots.txt`
- `/sitemap.xml`
- RSS/Atom feeds.
- JSON endpoints.

Do not fail the browser harness just because a browser-rendered XML/TXT page has no visual H1.

## Failure Triage

- If every route times out, check server/container readiness first.
- If only dynamic routes fail, check data, slugs, static params, and draft status.
- If admin fails, check Payload config, auth, env, database, and import map.
- If screenshots are blank but HTML/status/source look healthy, rerun and compare browser console and CSS.
- If the harness is unstable, stop and fix the harness or mark the run blocked.

## Completion Evidence

Report:

- Base URL.
- Runtime command or container.
- Route set.
- Output folder.
- Summary file.
- Failures with exact URLs and likely layer.
- Remaining blocker, if any.
