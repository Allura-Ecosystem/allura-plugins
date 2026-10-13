# Adaptive cowork contract

Use one accountable owner for each deliverable. A persona names a responsibility;
it does not require a new process, model call, or runtime handoff.

## Routes

| Route | Trigger | Execution and evidence |
| --- | --- | --- |
| Quick | Clear, reversible, bounded work under existing authority | Owner completes it and runs the relevant check; no mandatory council |
| Standard | Feature, substantial artifact, or work spanning contracts | Owner plus independent reviewer for the affected concern |
| Sensitive | Security/tenant boundary, destructive operation, production change, locked strategy, external send, or promotion | Relevant specialist; verify authority before the gated action |

Risk takes precedence over size. A one-line authorization change is sensitive.
Unknown scope gets focused recon; report length and persona count are not complexity.
Carry existing explicit user authorization forward. Ask only for missing authority,
missing acceptance criteria, or a consequential unresolved choice. A policy check
does not by itself require asking the user again.

## Context reuse

Hydrate once before planning. Pass a compact packet containing objective,
project, tenant, source revision, retrieval time, scope/authority, relevant source
paths, memory receipts or unavailable reason, decisions, acceptance and checks.
Reuse it only within the same project, tenant, task scope and source revision.
Refresh affected context after source edits, changed approvals, new blockers,
contradicting evidence, or tool/permission changes. Never reuse cached authorization
as proof that a live protected operation is currently permitted. Refresh current
external facts when needed. Do not bootstrap the whole team on every iteration.

## Model selection

Default to the user's configured model. Claude agent definitions use `model: inherit`;
Codex dispatch omits model overrides; OpenCode agents omit the optional model field.
These are runtime conventions, not interchangeable provider IDs. Direct model APIs
must receive an explicitly configured, supported model identifier.

Choose an override only when authorized and available. Evaluate fast models for
retrieval/extraction, strong general models for production, reasoning models for
hard diagnosis, and image-capable models for visual inspection. Names and persona
seniority are not capability evidence. Do not automatically downgrade review or
assume a different model makes a review independent. Use a separate review context
and actual tests/artifacts. Preserve the configured model if no evaluated binding
exists; report unsupported capability rather than silently substituting.

## Parallel work and handoffs

Run independent work concurrently only when it reduces the critical path. Give
each worker explicit output/file ownership, inputs, acceptance criteria and a budget.
Do not concurrently edit shared files. Dependent work waits for approved inputs.
Reviewers report findings; the producer fixes them. Reuse an existing worker for
follow-up instead of starting a new conversation to repeat its context.

Keep work in its current runtime unless a required tool, isolated context, or
measured quality benefit warrants a handoff. Route by demonstrated capability and
available tools, not blanket claims that one vendor writes and another reasons.

## Evidence and measurement

Check progress against acceptance criteria. Bound retries; surface repeated failure
with evidence and the smallest unblock action. Never equate budget exhaustion,
definition loading, or a drafted plan with completed execution.

Record elapsed time, preparation time, model/runtime, handoff count, tool failures,
review rounds, acceptance result, and token/cost usage when actually available.
Unknown measurements stay unknown. Compare representative tasks with identical
acceptance criteria before claiming faster or cheaper delivery. Offline contract
checks do not demonstrate live model performance.

Write one concise episodic outcome after substantive verified work, including
degraded memory status when relevant. Authenticate `user_id`; put the role in
`metadata.agent_id`. Default to `allura-system` unless the project declares another
authorized tenant. Human curators alone approve semantic promotion. Append-only
history, external-send authority and domain safety boundaries remain mandatory.
