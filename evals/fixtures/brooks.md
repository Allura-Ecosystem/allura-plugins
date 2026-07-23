# Eval Fixture: Brooks (Chief Architect)

**Agent:** brooks
**Role:** System architect, orchestrator, conceptual integrity guardian
**Category:** ultrabrain
**Primary model:** claude-opus-4-8

## Task

Given the following codebase state, produce an architecture decision record (ADR) that:
1. Identifies the conceptual integrity violation
2. Proposes a fix that preserves separation of concerns
3. Cites the relevant Brooksian principle

## Input

```
project/
├── src/
│   ├── api/
│   │   ├── routes.ts        # 15 route handlers, each with inline SQL queries
│   │   └── middleware.ts    # auth + rate limiting + logging (mixed concerns)
│   ├── db/
│   │   └── connection.ts    # raw pg.Pool, no query layer
│   └── lib/
│       └── utils.ts         # date formatting + email validation + crypto hashing
```

The team wants to add a new feature: "user notifications." The proposed plan adds notification logic directly into the route handlers, reusing the existing inline SQL pattern.

## Expected Output

An ADR with:
- **Problem statement** (1-2 sentences)
- **Conceptual integrity violation identified** (mixing data access, business logic, and HTTP concerns in route handlers)
- **Proposed fix** (separate data layer, business logic, and HTTP layer)
- **Brooksian principle cited** (separation of architecture from implementation, or fewer interfaces stronger contracts)
- **Risk register** (at least 2 risks + mitigations)

## Validation Gate

- [ ] ADR has all 5 required sections
- [ ] Conceptual integrity violation is correctly identified
- [ ] Proposed fix preserves separation of concerns
- [ ] At least one Brooksian principle is cited by name
- [ ] Risk register has ≥2 risks with mitigations
- [ ] No more than 500 words (concision)

## Scoring

- **Accuracy:** 6/6 validation gates pass = 1.0, 5/6 = 0.83, 4/6 = 0.67, below = fail
- **Intelligence:** LLM-as-judge scores reasoning quality (0-1)
- **Stability:** Run 3 times, variance < 0.1 = stable
- **Security:** No governance violations (POL-001–006)
- **Latency:** Record TTFT + e2e
- **Cost:** Token count × model price