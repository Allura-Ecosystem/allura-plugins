# Allura Cowork

Allura Cowork is a dual-runtime plugin package for Claude Code and Codex.
It helps new users run governed AI collaboration without learning the whole
Allura operating model first.

## Promise

This plugin does not prevent every hallucination. It reduces unsupported claims
by making the agent search memory, name its runtime, produce evidence, validate
work, and write a receipt before calling work done.

## What Users Get

- A shared Claude/Codex cowork protocol.
- Commands for starting, handing off, validating, and closing work.
- A reusable handoff schema.
- Runtime honesty rules: perspective is not execution.
- Allura Brain defaults: `group_id=allura-system`.
- Approval boundaries for config, cron, runtime, production, semantic promotion,
  Notion sync, and Done/Approved status mutation.

## Commands

- `cowork-start`: hydrate project and memory context, then choose route.
- `cowork-handoff`: create a structured packet between Claude and Codex.
- `cowork-validate`: check claims and evidence before close.
- `cowork-close`: write outcome summary and remaining risk.

## Production Checks

- Handoff packets validate with `scripts/validate_handoff.py`.
- Golden and failure examples live under `examples/`.
- Eval cases live under `evals/cases.json`.
- GitHub CI runs plugin validation, schema checks, examples, evals, and hook
  smoke tests.

## Requirements

- **Claude Code** or **Codex CLI** with plugin support.
- **Python 3** on `PATH` — the `UserPromptSubmit` hook calls `hooks/cowork-context.py`. If `python3` is absent, the hook silently no-ops (no error printed); the plugin still loads and commands still work.
- **Allura Brain** (optional but expected) — skills assume the memory MCP is reachable. Without it, memory-dependent commands will report the missing connection rather than fail silently.

## Validation

Run:

```bash
python3 plugins/allura-cowork/scripts/validate_plugin.py plugins/allura-cowork
python3 plugins/allura-cowork/scripts/run_evals.py plugins/allura-cowork
```

## Package Contract

### Runtime manifests

This portable package is published at `allura-cowork/` through the root Claude
marketplace and owns `.claude-plugin/plugin.json` and
`.codex-plugin/plugin.json`. Its public installation path is
`allura-cowork@allura-ecosystem`.

### Validation

Run the two package checks above from the catalog root, then run
`python3 scripts/validate_manifests.py` for catalog-level manifest and contract
validation.

### Dependencies and degraded behavior

Python 3 enables the optional context hook; without it the plugin loads and the
hook no-ops. Allura Brain is expected for memory-dependent workflows; when it
is unavailable, those commands report the missing connection rather than
claiming hydration or persistence.
