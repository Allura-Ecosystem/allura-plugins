# Blueprint

> AI-assisted working document. Runtime schemas, validated package contents,
> and Ronin's approved decisions override this draft.

## Product Intent

Provide one trusted Allura-Ecosystem catalog from which Claude and Codex can
install the same approved Allura capabilities.

## Users

- Ronin, as catalog owner and release approver.
- Claude and Codex desktop/CLI runtimes.
- Allura package maintainers in product repositories.

## Outcomes

1. One organization-owned catalog replaces divergent home-local authorities.
2. Capability parity is explicit, including justified runtime asymmetry.
3. Package validation and integration evidence precede installation.
4. Automated checks expose future drift before release.

## Non-Goals

- Making Claude and Codex manifest formats artificially identical.
- Moving product source ownership into this catalog.
- Publishing packages before secret scanning and integration validation.
