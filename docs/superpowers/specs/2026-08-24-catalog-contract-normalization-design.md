# Catalog Contract Normalization

## Status

Proposed design approved in principle. No package moves are authorized by this document.

## Goal

Make each distributable Allura unit self-contained and independently verifiable while retaining `allura-plugins/` as the single catalog and release-control root. Existing public install paths remain valid during the transition.

## Scope

The governed units are:

1. `allura-cowork/` — portable Claude/Codex plugin.
2. `team-durham/` — portable Claude/Codex plugin with optional integrations.
3. `team-ram-coding/` — portable Claude/Codex plugin with optional Allura services.
4. `plugins/hermes-allura-brain/` — Hermes-native provider.
5. `allura/` — internal Codex support pack; explicitly non-public until its manifest is complete.

`allura-plugins/` owns marketplace metadata, shared validation, repository-level tests, release evidence, and documentation. `mortagate/` and the standalone `allura-team-ram/` harness are outside this catalog.

## Decision

Normalize packages in place rather than create a `packages/` subtree or split repositories. Every public package must provide: a runtime manifest, package README, version declaration, validation entry point, declared optional dependencies, and a compatibility statement. Runtime-specific implementation remains within the package.

## Boundary Contract

The root catalog may reference a package only through that package's manifest and documented release metadata. A package may rely on Allura Brain or optional external services, but must describe the degraded behavior when those services are absent. Cross-package imports and undocumented relative-path coupling are prohibited.

## Migration Sequence

1. Establish a machine-checkable package inventory and contract validator.
2. Normalize Allura Cowork as the reference package; verify marketplace discovery and local validation.
3. Apply the same contract to Team RAM Coding and Team Durham.
4. Apply the provider variant of the contract to Hermes.
5. Resolve `allura/` as either a complete public package or explicit internal support.
6. Repair version, command-count, and legacy-path documentation drift.

No folder moves occur in this sequence. A later proposal for a `packages/` subtree requires separate approval after compatibility validation.

## Validation

For each normalized package: manifest parses; all manifest paths resolve; README installation steps match catalog metadata; declared version surfaces agree or document intentional differences; package validation passes; and the package remains discoverable at its current path.

## Risks

- Hermes has a distinct runtime contract and must not be forced into the Claude/Codex manifest shape.
- Optional Brain and third-party integrations must fail visibly without preventing core package loading.
- Legacy paths and version drift can make a structurally valid package unreleasable.

## Non-goals

- Moving all packages into a new subtree.
- Splitting packages into separate repositories.
- Changing product behavior or runtime capabilities.

## References

- `docs/RISKS-AND-DECISIONS.md` — AD-005
- `docs/DESIGN-PLUGIN-CATALOG.md`
- `.claude-plugin/marketplace.json`
