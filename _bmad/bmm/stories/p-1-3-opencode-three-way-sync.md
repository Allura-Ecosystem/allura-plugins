# Story P-1.3 — OpenCode Three-Way Sync

**Status:** Planned
**Owner:** Woz + Knuth
**Depends on:** P-1.1
**Blocks:** P-1.5

## Outcome

Claude, Codex, and OpenCode plugin surfaces are reconciled; drift is detected and reported rather than silently accumulated.

## Acceptance Criteria

- [ ] A three-way sync script compares Claude-native, Codex-native, and OpenCode-native plugin surfaces.
- [ ] Missing files, mismatched versions, and divergent definitions are detected.
- [ ] A drift report identifies differences and remediation steps.
- [ ] CI runs the sync check on every push and blocks on drift.
- [ ] The check runs locally through a documented command.
