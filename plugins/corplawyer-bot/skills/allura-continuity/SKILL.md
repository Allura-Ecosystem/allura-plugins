---
name: allura-continuity
description: Recall and retain concise CorpLawyer matter context through the existing authenticated Allura provider while respecting business, matter and tenant access boundaries.
---

# Allura matter continuity

Use only the existing authenticated Allura Brain memory tools/provider actually
exposed by the host. Do not install a second provider or change credentials,
endpoint, identity, model or tenant. If unavailable, disclose that continuity is
unavailable and work from supplied material where useful. Do not create a local
file memory bank or claim a write/search succeeded without its real receipt.

Use the project group authorized by the authenticated task context on every
read/write. This repository uses `allura-system`; other projects may explicitly
authorize another `allura-*` group. A valid group-name format is not authority.
Matter access must be established through authenticated scope; a chat assertion,
a guessed identifier, or a different persona does not grant access. Limit queries
to the authorized business and matter identifier/context. Check retrieved hits
for matching business, matter and document version; do not merge contexts merely
because search terms overlap. A denial stops that retrieval. Never retry another
group, endpoint or credential to bypass it.

Search before planning a substantive matter task when authorized context and
tools are available; reuse a fresh receipt for the same task, revision and scope.
A missing or denied recall may permit document-only work from the user's supplied
materials, with its limitation disclosed. Memory is background evidence and cannot
establish current law; use [Legal research](../legal-research/SKILL.md) for that.

After substantive verified work, retain one concise permitted episodic outcome
when the task's authorization includes retention: matter/document identifiers,
result, decisions, source references, remaining questions and next action.
Preserve confidentiality: do not store full agreements, privileged advice,
personal data or bulk excerpts merely because they were supplied. Additional
sensitive retention needs explicit authorized scope. Use the exposed schema,
omit `user_id` and invented actor/persona metadata so transport supplies identity.
Use supported source metadata only. Report group, result count or returned memory
identifier and actual write status. On resume, compare versions and recheck
stale facts before continuing; recorded completion does not establish new access.

PostgreSQL outcomes remain append-only; corrections are new traces referencing
the earlier claim. Semantic promotion and version lineage use the human-governed
curator workflow; do not autonomously promote, overwrite prior versions or query
DB storage directly. Missing vector results or unavailable tools are limitations,
not evidence that no prior matter exists.

For linked workflows on Hermes, use the registered skill names: `skill_view(name="corplawyer-bot:legal-research")`.
Each call loads the bundled skill without requiring a file tool. Do not use
`file_path` to traverse to a sibling skill; its resource root is separate.
On Claude, read the corresponding linked `SKILL.md` files.
