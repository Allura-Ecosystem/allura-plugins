# Eval Fixture: Woz (Primary Builder)

**Agent:** woz
**Role:** Implementation, testing, code delivery
**Category:** builder
**Primary model:** claude-sonnet-4

## Task

Implement a `validateEmail` function in TypeScript that:
1. Accepts a string and returns a `Result` type (`{ ok: true, value: string } | { ok: false, error: string }`)
2. Validates against RFC 5322 simplified rules (local part + @ + domain with at least one dot)
3. Rejects empty strings, strings without @, and domains without a dot
4. Includes 5 unit tests (2 valid, 3 invalid cases)

## Expected Output

A single TypeScript file with:
- The `Result` type definition
- The `validateEmail` function
- 5 unit tests using a standard test framework (vitest/jest)
- All tests passing when run

## Validation Gate

- [ ] `Result` type is a discriminated union
- [ ] `validateEmail` handles all 3 invalid cases (empty, no @, no dot in domain)
- [ ] `validateEmail` accepts valid emails
- [ ] Exactly 5 unit tests (2 valid, 3 invalid)
- [ ] Code compiles with `tsc --noEmit`
- [ ] Tests pass with `vitest run` or `jest`

## Scoring

- **Accuracy:** 6/6 validation gates pass = 1.0
- **Intelligence:** Code quality (readability, naming, no unnecessary complexity)
- **Stability:** Run 3 times, same implementation = stable
- **Security:** No `eval`, no `any` types, no unsafe patterns
- **Latency:** Record TTFT + e2e
- **Cost:** Token count × model price