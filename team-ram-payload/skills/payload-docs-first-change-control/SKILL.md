---
name: payload-docs-first-change-control
description: Use before changing architecture, schema, APIs, routes, Payload models, content blocks, governance rules, or business logic in docs-first Payload projects.
---

# Payload Docs First Change Control

Use this when a Payload repo has documentation-first governance or when a change touches durable project truth.

## Required Order

1. Read the repo's AI or agent guidelines.
2. Identify the governing artifact.
   - Design intent: `BLUEPRINT.md`.
   - Topology and integrations: `SOLUTION-ARCHITECTURE.md`.
   - Feature behavior: `DESIGN-*.md`.
   - Requirement coverage: `REQUIREMENTS-MATRIX.md`.
   - Field, enum, relationship, and nullability truth: `DATA-DICTIONARY.md`.
   - Accepted tradeoffs, rejected paths, and risks: `RISKS-AND-DECISIONS.md`.
3. Update docs before or alongside code.
4. Keep links relative where possible.
5. Include the repo-required AI-assisted notice when drafting or substantially changing docs with AI.

## Conflict Rule

Actual code wins over stale prose, but do not silently choose between conflicting authorities. Stop, name the conflict, and either fix the docs or ask for the decision.

## Traceability Checklist

- Every new field appears in code, generated types, schema docs, and Data Dictionary.
- Every enum value is documented exactly.
- Requirement changes appear in the Requirements Matrix.
- Architecture decisions have a decision entry.
- New known failure modes have risk entries.
- Validation evidence points to real command output or a real user-path check.
