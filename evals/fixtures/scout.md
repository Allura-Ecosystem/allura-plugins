# Eval Fixture: Scout (Recon & Discovery)

**Agent:** scout
**Role:** File discovery, pattern grep, risk scanning
**Category:** recon
**Primary model:** claude-haiku-4-5

## Task

Given a codebase with the following structure, identify:
1. All files that import `fs` or `fs/promises` (filesystem access)
2. Any files that use `eval()` or `new Function()` (security risk)
3. Any `.env` files that are NOT in `.gitignore` (secret leak risk)

## Input (simulated file tree)

```
project/
├── src/
│   ├── config.ts          # imports fs/promises to read config
│   ├── loader.ts          # uses eval() to parse dynamic expressions
│   ├── utils.ts           # imports fs for path operations
│   └── safe.ts            # no fs, no eval
├── .env                   # exists, NOT in .gitignore
├── .gitignore             # exists, does not contain .env
└── tests/
    └── config.test.ts     # imports fs/promises
```

## Expected Output

A structured report with:
- **File paths** for each finding (exact paths)
- **Risk level** for each finding (low/medium/high)
- **Recommendation** for each finding (1 sentence)

## Validation Gate

- [ ] Identifies all 3 files importing fs/fs-promises (config.ts, utils.ts, config.test.ts)
- [ ] Identifies loader.ts as using eval()
- [ ] Identifies .env not in .gitignore as a secret leak risk
- [ ] Each finding has a risk level
- [ ] Each finding has a recommendation
- [ ] Does NOT flag safe.ts (no false positives)

## Scoring

- **Accuracy:** 6/6 validation gates pass = 1.0
- **Intelligence:** Report clarity and precision
- **Stability:** Run 3 times, same findings = stable
- **Security:** Correctly identifies security risks
- **Latency:** Record TTFT + e2e (recon should be fast — haiku tier)
- **Cost:** Token count × model price