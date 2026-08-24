# Story P-2.3 — Connection Health and Retry — Degraded-State Handling

**Status:** Planned
**Owner:** Woz + Bellard
**Depends on:** P-2.1
**Blocks:** —

## Outcome

When Allura Brain is down, the provider detects it, retries with backoff, and surfaces a degraded state rather than hanging or crashing.

## Acceptance Criteria

- [ ] Brain-down is detected within a configurable timeout.
- [ ] Retry uses exponential backoff with a maximum retry count.
- [ ] After maximum retries, the provider returns a typed degraded-state response.
- [ ] Hermes receives a clear availability message and can proceed without memory.
- [ ] Degraded state is logged for observability.
