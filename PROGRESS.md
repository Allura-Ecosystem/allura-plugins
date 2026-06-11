# Progress

## Definition of Done

- [ ] Approved inventory is recorded with provenance.
- [ ] Canonical packages pass Claude and Codex validation.
- [ ] Claude migration passes restart verification.
- [ ] Codex migration passes restart verification.
- [ ] Cowork, Brain, and governance integration evidence passes.
- [ ] CI and local drift audits pass.
- [ ] Ronin approves release or public visibility.

## Phases

- [x] Phase 0: Approve organization ownership and create private catalog.
- [x] Phase 1: Snapshot and inventory live installations.
- [ ] Phase 2: Select and restore canonical packages.
- [ ] Phase 3: Validate packages and repair incompatibilities.
- [ ] Phase 4: Migrate and verify Claude.
- [ ] Phase 5: Migrate and verify Codex.
- [ ] Phase 6: Run cross-runtime integration proof.
- [ ] Phase 7: Install drift prevention and close governance records.

## Current Gate

Select canonical candidates using upstream repository history, package hashes,
manifest validation, and tests. Do not copy packages based only on timestamps
or version strings.
