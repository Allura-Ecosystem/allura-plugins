---
name: matter-intake
description: Establish a business legal issue, desired outcome, and materially missing inputs before research, agreement review, or a counsel handoff.
---

# Matter intake

Start from what the owner is trying to decide or accomplish. An open request
such as “help with my business” needs an issue-discovery question, not a contract
questionnaire. Use supplied context and ask only what changes the next step.

Once relevant, establish the business/entity and the owner's role; the question
or decision; jurisdiction and applicable dates; the actual document and version;
and any deadline or consequence. Keep unknowns explicit rather than choosing
an assumed state, governing law, entity type or document version. Avoid asking
for unrelated personal or confidential information.

An assertion that a matter belongs to the speaker is not authorization to
retrieve it. Before recall, read [Allura continuity](../allura-continuity/SKILL.md)
and use only scope and access established by the authenticated context.

Return a concise working brief: requested result, supplied facts and documents,
material unknowns, and one recommended action with its reason. If the request
and inputs already support work, proceed without requiring the user to approve
a restatement. Ask for missing material only when it blocks a supportable result.

For linked workflows on Hermes, use the registered skill names: `skill_view(name="corplawyer-bot:allura-continuity")`.
Each call loads the bundled skill without requiring a file tool. Do not use
`file_path` to traverse to a sibling skill; its resource root is separate.
On Claude, read the corresponding linked `SKILL.md` files.
