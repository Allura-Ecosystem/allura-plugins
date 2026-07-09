---
name: payload-governed-development
description: Use before building, modifying, reviewing, or debugging Payload CMS 3 projects, especially collections, globals, blocks, Lexical content, access control, hooks, generated types, seeds, and frontend rendering.
---

# Payload Governed Development

Use this before touching Payload code, schema, admin config, content models, frontend rendering, seeds, or deployment behavior.

## Preflight

1. Run `payload-project-hydration` if this is a new or resumed repo context.
2. Run the Allura memory gate when memory tools are available.
3. Read the source-of-truth docs the repo actually has.
   - `AI-GUIDELINES.md`
   - `IMPLEMENTATION-SOURCE-OF-TRUTH.md`
   - `BLUEPRINT.md`
   - `SOLUTION-ARCHITECTURE.md`
   - `DATA-DICTIONARY.md`
   - `REQUIREMENTS-MATRIX.md`
   - `RISKS-AND-DECISIONS.md`
   - relevant `DESIGN-*.md`
4. Inspect actual code before trusting stale prose.
   - Payload config.
   - Collections.
   - Globals.
   - Blocks.
   - Generated types.
   - JSON schema exports if present.
   - App Router route files.

## Payload Rules

- Use Payload 3 typed configs: `CollectionConfig`, `GlobalConfig`, and `Block`.
- Blocks need stable `slug` and `interfaceName`.
- Access starts restrictive and opens only when documented.
- Media fields should require meaningful alt text unless explicitly decorative.
- Rich text should use approved Lexical features and preserve semantic heading order.
- Put defaults and normalization in `beforeChange` hooks.
- Put revalidation and side effects in `afterChange` hooks.
- Do not add collections, globals, blocks, fields, enum values, routes, or admin surfaces unless they are documented or approved.
- After schema/admin config changes, run generated-type/import-map commands when the repo provides them.

## Collection And Block Heuristic

- If it owns a URL or lifecycle, it is probably a collection.
- If it only appears inside a page layout or component, it is probably a block or array field.
- If it controls site-wide configuration, it is probably a global.
- If it is a short closed vocabulary, prefer a select enum before inventing a collection.

## Documentation Coupling

When the repo has docs-first governance, update docs in the same work unit:

- Field truth goes in the Data Dictionary.
- Requirement impact goes in the Requirements Matrix.
- Structure or integration changes go in the Solution Architecture.
- Design intent goes in the Blueprint or area design doc.
- Decisions, rejected options, and risks go in Risks and Decisions.

## Done Standard

Types regenerate when needed, implementation compiles, docs match code, route or admin behavior is verified, and evidence is recorded.
