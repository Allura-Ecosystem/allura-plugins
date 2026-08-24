# Story P-2.2 — Authentication and Tenant Scoping — Group_id Propagation

**Status:** Planned
**Owner:** Brooks + Knuth
**Depends on:** P-2.1
**Blocks:** P-2.3

## Outcome

`group_id` is inherited from trusted delegation context, not self-asserted by a subagent. Cross-tenant access is denied.

## Acceptance Criteria

- [ ] `group_id` passes through the delegation chain and children inherit the parent tenant.
- [ ] A subagent on one tenant cannot retrieve another tenant's memories.
- [ ] Missing `group_id` returns a typed error, never a default tenant.
- [ ] Tenant forgery is denied and logged.
