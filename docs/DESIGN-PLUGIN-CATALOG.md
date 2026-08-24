# Design: Plugin Catalog

> AI-assisted working document. Exact behavior remains subject to runtime
> schema validation.

## Repository Shape

```text
.
|-- .agents/plugins/marketplace.json
|-- .claude-plugin/marketplace.json
|-- docs/
|-- plugins/
|   `-- <plugin-name>/
`-- scripts/
```

## Catalog Rules

1. Every catalog entry resolves to an existing package directory.
2. Package folder and manifest names use lower-case hyphen-case.
3. Versions for a portable package match across runtime manifests.
4. Runtime-specific hooks remain in runtime-specific files.
5. Absolute home-directory paths are prohibited.
6. Secrets, credentials, tokens, and private customer data are prohibited.
7. A package records its upstream repository and revision before release.
8. A public package owns its runtime manifest, README, validation entry point,
   optional-dependency declaration, and compatibility statement.
9. The catalog root owns marketplace metadata and shared release validation;
   packages do not depend on undocumented paths into one another.
10. Native providers may use a provider-specific manifest contract and are not
    required to imitate portable Claude/Codex package metadata.

## Initial Candidate Inventory

The first governed sync pass should begin with the agents roster in `docs/AGENTS-INVENTORY.md` before extending the same control plane to skills and commands.


| Capability | Claude | Codex | Classification |
|---|---|---|---|
| `allura-cowork` | Plugin | Plugin | Portable |
| `allura-governance` | Plugin | Plugin | Portable after hook repair |
| `allura-brain` | Plugin | Native MCP | Intentional asymmetry |
| `team-ram-coding` | Plugin | Plugin | Portable candidate |
| `team-durham` | Plugin | Plugin | Portable candidate |
| `team-durham-app-audit` | Plugin | Plugin | Portable candidate |
| `allura` | Optional | Optional | Product/docs asset |
| `team-ram-payload` | Optional | Optional | Project-specific |

The inventory remains provisional until package hashes, manifests, tests, and
upstream provenance are recorded.

## Failure Behavior

Validation failure blocks catalog publication and runtime migration. One
runtime may be rolled back independently while Allura Brain remains available
through its governed MCP gateway.
