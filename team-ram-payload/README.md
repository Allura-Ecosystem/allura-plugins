# Team RAM Payload

Team RAM Payload is a local Codex plugin for governed Payload CMS and Next.js/Payload projects.

It packages the reusable parts of the Difference Driven build without making that client-specific harness global. Use it when a Payload project explicitly wants Team RAM routing or when the user asks for Team RAM help in a Payload repo.

## What It Provides

- Team RAM routing as an operating lens: Brooks, Jobs, Woz, Scout, Pike, Fowler, Bellard, Carmack, Knuth, and Hightower.
- Allura/RuVix-style governance: search context first, prove changes with validation, keep project boundaries isolated, and log important outcomes when memory tools are available.
- Payload 3 guardrails for collections, globals, blocks, Lexical, media, access control, hooks, generated types, and App Router rendering.
- Debug-first workflow for route, admin, build, Docker, and deployment failures.
- Route smoke guidance learned from the Difference Driven build: guarded route roots, fresh output, request probes for XML/TXT assets, and no stale-path assumptions.

## Boundaries

- This plugin is opt-in. It does not mean every Payload project globally uses Team RAM.
- If a repo has its own `AGENTS.md`, `.opencode/`, `.agents/`, `.claude/`, or docs, those local files remain the source of truth.
- Allura memory is context, not proof of done. Command output, health checks, tests, screenshots, source docs, or user approvals prove done.
- Do not claim a Team RAM subagent, OpenCode run, Allura search, memory write, test, or browser check happened unless a real tool call happened.

## Starter Flow

1. Use `team-ram-payload` to start the operating loop.
2. Use `payload-project-hydration` to map the repo.
3. Use `payload-governed-development` before schema, route, block, API, or content-model changes.
4. Use `payload-debug-first` when anything is broken or uncertain.
5. Use `payload-route-smoke-harness` for route/browser proof.
6. Use `payload-session-closeout` before handing back the work.

The helper script `scripts/probe-payload-project.sh` is read-only and prints the basic repo shape for a Payload session.
