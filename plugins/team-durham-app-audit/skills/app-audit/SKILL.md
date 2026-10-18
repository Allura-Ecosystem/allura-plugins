---
name: app-audit
description: Audit a live brand app or website for brand drift and UX regressions against a locked brand-truth.json. Use when the user says "audit {brand}", "check compliance for {brand}", "ux test {brand}", "review {brand}'s site", or asks to check whether a deployed app still matches the brand guidelines. For Team Durham brand engagements stored under clients/{brand}/.
---

# Team Durham App Audit

Audit a deployed brand application for compliance drift (color, type, logo, voice) and UX regressions, comparing the live surface against the brand's locked `brand-truth.json`.

## When to use

Trigger when the user wants to verify a live app/site still matches an established brand: "audit ember-fold", "check compliance for amaysinpro", "ux test {brand}", "is the site still on-brand".

## Inputs

- **brand-slug** (required): folder name under `clients/`.
- **target URL** (required for live capture): the deployed site/app. Ask if not provided.

## Workflow

1. **Lock check.** Read the brand truth: `clients/{brand}/*brand-truth.json`. If absent, stop — brand truth must be locked before auditing (STP before pixels).
2. **Capture.** Use browser automation to screenshot the key surfaces (landing, primary CTA, one interior view).
3. **Compare.** Evaluate observed vs. expected for: color palette, typography, logo usage and clear-space, and voice/tone. Record each as a finding with severity.
4. **Report.** Output a findings table ranked by severity with specific, actionable fixes. Save audit findings and captured evidence to `clients/{brand}/audits/`. Visual fixes require a separately approved implementation task.
5. **Evidence (optional).** If Allura Brain is reachable, log `AUDIT_DRIFT_DETECTED` with `group_id: allura-team-durham`. If unreachable, note and continue.

## Roles (reference)

Munari audits read-only; Rand tests UX read-only; Glaser prepares visual fixes for a separately approved task; Kotler owns evidence and governed outcome logging. These are role assignments, not claims that agents have been invoked.

## Governance

Read-only on the customer's live app. Use `group_id: allura-team-durham` only with authenticated access to that tenant. Never switch credentials or tenant to bypass denial. Events are append-only in PostgreSQL; semantic changes use the governed curator workflow and immutable SUPERSEDES lineage (RuVector/PostgreSQL is the default, Neo4j is fallback only). Omit user_id and unverified agent_id attribution; authenticated transport owns identity. Never directly mutate the knowledge graph, approve promotion, or push changes to a customer site from this skill.

Live capture requires an available browser tool; memory logging requires an authorized Allura Brain connection. If either is unavailable or denied, state the limitation and report only evidence actually observed. A locked brand truth is still required before auditing.
