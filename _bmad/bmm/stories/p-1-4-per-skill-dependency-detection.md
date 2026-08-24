# Story P-1.4 — Per-Skill Dependency Detection

**Status:** Planned
**Owner:** Woz + Pike
**Depends on:** P-1.1
**Blocks:** P-1.5

## Outcome

Each skill visibly no-ops when a required service is absent rather than crashing or producing misleading errors.

## Acceptance Criteria

- [ ] Every skill declares service dependencies in its manifest or package contract.
- [ ] Skills check service availability at startup and give a clear no-op message when absent.
- [ ] No skill crashes or produces misleading output when a dependency is missing.
- [ ] Dependency detection is tested with services absent and present.
