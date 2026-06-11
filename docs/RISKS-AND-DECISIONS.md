# Risks and Decisions

## Decisions

### AD-001: Dedicated Organization Catalog

**Date:** 2026-06-11  
**Decision:** Use `Allura-Ecosystem/allura-plugins` as the catalog authority.  
**Reason:** Plugin release cadence and validation should not be coupled to the
Allura Memory product repository.

### AD-002: Private First

**Date:** 2026-06-11  
**Decision:** Keep the repository private during inventory and validation.  
**Reason:** Existing package copies have not completed provenance, secret, and
path scans.

### AD-003: Capability Parity

**Date:** 2026-06-11  
**Decision:** Align capabilities, not implementation mechanics.  
**Reason:** Claude and Codex have different plugin, hook, and MCP surfaces.

## Risks

| ID | Risk | Mitigation |
|---|---|---|
| RK-01 | A newer timestamp hides older behavior. | Compare upstream Git revisions, tests, manifests, and hashes. |
| RK-02 | Claude and Codex hook schemas diverge. | Validate separately and maintain runtime-specific hook files. |
| RK-03 | A package contains secrets or absolute paths. | Block release on secret and path scans. |
| RK-04 | Global team plugins bypass project routing. | Separate installation availability from project activation policy. |
| RK-05 | Config text appears correct while runtime load fails. | Require native list output and restart verification. |
