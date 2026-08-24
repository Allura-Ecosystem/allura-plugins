# Story P-1.2 — Eval Fixture Expansion

**Status:** Planned
**Owner:** Woz + Fowler
**Depends on:** P-1.1
**Blocks:** P-1.5

## Outcome

Eval fixture coverage expands beyond the current five agents to cover all installed catalog agents with pass/fail evidence.

## Acceptance Criteria

- [ ] Eval fixtures exist for every agent defined in the catalog.
- [ ] Each fixture has a pass/fail verdict with evidence.
- [ ] Eval results are reproducible: the same input produces the same verdict.
- [ ] The eval CI lane runs on every push and reports coverage.
