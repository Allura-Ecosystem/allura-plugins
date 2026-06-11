# Data Dictionary

| Term | Definition |
|---|---|
| Catalog | The organization repository and its runtime marketplace manifests. |
| Package | A directory under `plugins/` containing one Allura capability. |
| Portable package | A package validated for both Claude and Codex. |
| Runtime-only package | A package intentionally supported by one runtime. |
| Capability parity | Equivalent user-visible behavior despite different runtime integration. |
| Upstream | Product repository that owns the package's source implementation. |
| Provenance | Upstream repository, revision, version, and validation evidence. |
| Desired inventory | Approved packages expected to be available in a runtime. |
| Live inventory | Packages reported installed and loaded by native runtime commands. |
| Drift | A mismatch among catalog, package contents, configuration, or live runtime state. |
| Evidence packet | Saved validation, test, integration, and restart results for a release. |
