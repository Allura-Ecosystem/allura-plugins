# Allura Cowork Evals

These evals check whether the plugin rules catch common failure modes.

## What Evals Cover

- Fake Done claims
- Missing Allura Brain search
- Unrun validation
- Runtime perspective presented as execution
- Approval-required changes treated as safe
- Public or external sends without approval

## Run

```bash
python3 plugins/allura-cowork/scripts/run_evals.py plugins/allura-cowork
```

## Passing Standard

Every eval case must define:

- the risky prompt;
- the risk being tested;
- expected guardrail language;
- expected status: `PASS`, `WATCH`, or `BLOCKED`.

The eval runner verifies that those expectations are represented in the plugin
skill, command docs, or examples. It does not call an LLM and does not claim a
model passed live behavioral testing.
