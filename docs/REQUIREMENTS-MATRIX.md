# Requirements Matrix

| ID | Requirement | Acceptance Evidence |
|---|---|---|
| FR-01 | The catalog is owned by `Allura-Ecosystem`. | GitHub repository metadata |
| FR-02 | Claude and Codex have explicit catalog manifests. | Schema validation |
| FR-03 | Every catalog entry resolves to a real package. | Catalog audit script |
| FR-04 | Portable package versions remain aligned. | Cross-manifest comparison |
| FR-05 | Runtime differences are documented. | Classification inventory |
| FR-06 | Existing runtime state is recoverable. | Timestamped backup manifest |
| FR-07 | Both runtimes load the approved inventory after restart. | Native plugin list output |
| FR-08 | Cowork handoff works from Claude to Codex. | Saved integration evidence |
| FR-09 | Both runtimes access the same scoped Allura Brain. | Search/write receipts |
| FR-10 | Governance rejects an invalid operation in supported runtimes. | Rejection test evidence |
| FR-11 | Future drift fails visibly. | CI and local audit results |
| NFR-01 | No secrets or private data enter the catalog. | Secret scan |
| NFR-02 | Home paths are not embedded in release packages. | Path scan |
