---
name: legal-research
description: Verify business legal claims against current official sources with jurisdiction, effective dates, precise citations and clear limits when evidence is unavailable.
---

# Legal research

Define the question, jurisdiction, relevant date and facts before choosing
sources. Use an actually available web/search or official-source connector to
retrieve current legislation, regulations, court material or regulator guidance.
Prefer primary official sources and read the supporting passage, not a search
snippet. Check effective dates, amendments and whether guidance is binding.
A contract's governing-law clause is evidence of its text, not proof that every
mandatory rule or dispute is governed by that law.

For each material legal conclusion give a direct source URL, title/issuer,
section or paragraph, jurisdiction, access date and relevant effective date when
shown. Explain how the source applies to the supplied facts and mark uncertain
application. Distinguish law from official guidance, contract text, a proposal
and an assumption. Do not claim complete coverage from one retrieved page.

If current retrieval or required jurisdiction is unavailable, say what could
not be verified and identify the narrow research question still open. Continue
with document-based analysis where useful; do not manufacture citations or label
remembered information as current law. Research examples or supplied excerpts
can support a bounded exercise but cannot establish that live legal research ran.

For specialist handoff use [Counsel brief](../counsel-brief/SKILL.md). For memory
recall or outcome retention read [Allura continuity](../allura-continuity/SKILL.md).
Keep research scope tied to the user's question; research does not authorize
filing, negotiation, external communication or a change to business records.

For linked workflows on Hermes, use the registered skill names: `skill_view(name="corplawyer-bot:counsel-brief")`; `skill_view(name="corplawyer-bot:allura-continuity")`.
Each call loads the bundled skill without requiring a file tool. Do not use
`file_path` to traverse to a sibling skill; its resource root is separate.
On Claude, read the corresponding linked `SKILL.md` files.
