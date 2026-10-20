---
name: allura-cowork
description: Use when the user says cowork, co-work, Claude and Codex, Codex and Claude, pair Claude with Codex, handoff between Claude/Codex, or asks how to make multiple AI runtimes follow Allura rules. Coordinates both runtimes through Allura Brain, runtime honesty, validation evidence, and governed handoff receipts.
---

# Allura Cowork

Use this skill to coordinate Claude Code and Codex without pretending they are
the same runtime.

## Core Contract

Apply [Adaptive cowork](../../docs/ADAPTIVE-WORK.md): choose quick, standard, or
sensitive work by risk; reuse fresh scoped context; inherit the configured model;
keep one accountable owner and add independent review where the risk warrants it.

```text
Intent -> Project context -> Allura Brain -> Route -> Work -> Validate -> Receipt -> Handoff or close
```

Allura Brain is the shared memory layer. Claude and Codex are execution
surfaces. Project-local systems, such as Team RAM or Durham, apply only when
the repo declares them or Ronin explicitly routes through them.

## Chat interaction

On activation or an explicit menu/help/MH request, load `../allura-menu/SKILL.md`.
Use Next steps, Help with a prompt, Council, Work, Loop, Validate and More.
When Brooks or Kotler is directly addressed, load that lead's full installed role
and show its actual documented domain menu on activation, with these shared
choices under More. Apply the lead's voice in the main conversation as well as
relays; preserve selection, objective, decisions and next action through follow-ups
and compaction until the user changes route. Quoted mentions and discussion do not
activate or switch roles. Reuse a fresh scoped Brain receipt or one bounded query
for relevant decisions, blockers, outcomes and lessons. Distinguish a recalled
reflection with memory ID/date from current judgment, no relevant memory, pending,
or unavailable retrieval. Do not invent continuity or write startup chatter.
Clear requests proceed directly. Keep RAM and Durham as domain routes under
Allura; Council requires actual available specialists and preserves disagreement.
Prompt help and bounded loops run in conversation without an extra plugin.

## Cowork completeness check

Check these items internally before planning or handoff. Ordinary chat uses
concise natural prose with the active role, result and useful next action.
Emit the full header only for an explicit machine handoff or integration request.
Preserve any receipt explicitly required by the active project's AGENTS guidance.

```text
Cowork active.
Runtime: <Claude|Codex|OpenCode|OpenClaw|other>
Allura: <memory searched/not available + query or reason>
Project overlay: <Team RAM|Durham|TALON|IRIS|none|unknown>
Route: <who owns implementation + who reviews>
Validation: <commands, checks, screenshots, or evidence path>
Handoff target: <Claude|Codex|none>
```

## Runtime Honesty

- Say "Claude perspective" or "Codex perspective" only as a lens unless that
  runtime actually ran.
- Never claim a subagent, tool, MCP call, test, file edit, or handoff happened
  unless it actually happened.
- If a handoff is only written instructions, label it `Handoff packet`.
- If validation did not run, say exactly what is unvalidated.

## Allura Brain Rules

- Search before planning when prior work, people, dates, decisions, preferences,
  todos, or Allura governance are involved.
- Default scope: `group_id=allura-system`.
- Omit `user_id` so authenticated transport supplies the principal. Add persona
  attribution only where the verified schema accepts it; otherwise omit it.
- Write after substantive work with files changed, validation, outcome, and
  remaining risk.
- Raw episodic memory is evidence. It is not canonical promotion.

## Approval Boundaries

Explicit approval is required before:

- runtime or database mutation
- MCP config mutation
- cron mutation
- live hook installation or enforcement
- RuVix runtime enforcement changes
- semantic memory promotion
- Notion sync
- Done/Approved status moves
- public or external sends

Existing explicit authorization satisfies the relevant boundary within its scope.
Prepare and validate reversible local work before requesting any missing authority.

## Handoff Packet

Use `schemas/handoff.schema.json` for machine-shaped packets. For chat, use:

```markdown
## Allura Cowork Handoff

From: <runtime/persona>
To: <runtime/persona>
Goal: <one sentence>
Context searched: <queries + memory ids or unavailable reason>
Project overlay: <Team RAM|Durham|TALON|IRIS|none|unknown>
Files touched/read: <paths>
Decisions: <bullets>
Open risks: <bullets>
Validation run: <commands/results>
Next action: <single concrete step>
Memory status: <written/not written + id if available>
Approval needed: <yes/no + why>
```

Before accepting a machine-shaped packet, validate it:

```bash
python3 plugins/allura-cowork/scripts/validate_handoff.py <packet.json>
```

If validation fails, treat the cowork state as `BLOCKED` until the packet is
fixed or the missing evidence is explicitly acknowledged.

## Routing Defaults

These are domain suggestions, not mandatory vendor handoffs. Keep the current
runtime when its tools and evaluated capabilities meet the task. Apply the
adaptive contract before adding a second runtime or reviewer.

- Codex: repository edits, validation loops, code review, practical
  implementation, commits.
- Claude: synthesis, long-form docs, UX/design review, plugin packaging,
  critique, prose-heavy planning.
- Team RAM: project-local implementation when the repo declares RAM or Ronin
  routes there.
- Durham: brand, copy, product feel, design canon, and final brand-sensitive
  approval.
- TALON: deploy, runtime, API readiness, test gates, runbooks, and guardrails.

## User-Facing Promise

Say: "This plugin reduces hallucinated claims by requiring memory search,
evidence, validation, and receipts before work is called done."

Do not say: "This plugin prevents hallucinations."

## Production-Grade Behavior

- Use `docs/COMMAND-MENU.md` when a new user asks what to type.
- Use `docs/INSTALL.md` when installing into a new Claude/Codex environment.
- Use `examples/golden/` for normal handoffs.
- Use `examples/failure/` when memory, validation, or approval is missing.
- Use `evals/cases.json` to test whether the plugin catches fake Done claims,
  unsearched memory, unrun validation, and approval boundary crossings.
