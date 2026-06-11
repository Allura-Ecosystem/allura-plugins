# Solution Architecture

> AI-assisted working document. Runtime schemas and validated package contents
> are authoritative.

## Boundaries

Upstream product repositories own plugin source. This repository pins validated
release copies and publishes two catalog views:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`

Packages live under `plugins/<plugin-name>/`. A portable package may contain
both `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Runtime-only
packages must be explicitly classified.

## Installation Flow

1. Upstream package is selected by evidence, not filesystem timestamp.
2. Package is copied into the catalog with provenance recorded.
3. Claude and Codex manifests are validated independently.
4. Catalog CI verifies paths, versions, package names, and policy fields.
5. Each runtime installs through its native plugin command.
6. Restart and integration evidence confirms actual load state.

## Brain Boundary

Allura Brain capability parity does not require identical packaging. Claude may
use an `allura-brain` plugin while Codex uses its native MCP configuration.
Both must connect to the same governed gateway with `group_id` and `user_id`.

## Release Authority

Ronin approves inventory and release. Validation success is technical evidence,
not release approval.
