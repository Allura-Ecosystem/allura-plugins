# Allura Cowork Command Menu

Use these commands as the user-facing entry points.

## Start

```text
cowork-start: Help me run this task with Claude and Codex.
```

Use when a user has a task and does not know which runtime should own it.

## Handoff

```text
cowork-handoff: Create a Codex handoff for this Claude plan.
cowork-handoff: Create a Claude review handoff for this Codex patch.
```

Use when work crosses runtime boundaries.

## Validate

```text
cowork-validate: Check whether this Done claim is supported.
```

Use before accepting a result, especially when tests, memory, or external tools
are mentioned.

## Close

```text
cowork-close: Close this cowork task with receipts and remaining risk.
```

Use after validation, not before.

## Status Words

- `PASS`: evidence supports the claim.
- `WATCH`: usable but residual risk remains.
- `BLOCKED`: missing evidence, missing approval, or unsupported Done claim.

## Default Promise

Say:

```text
Allura Cowork reduces hallucinated claims by requiring memory search, evidence,
validation, and receipts before work is called done.
```

Do not say:

```text
Allura Cowork prevents hallucinations.
```
