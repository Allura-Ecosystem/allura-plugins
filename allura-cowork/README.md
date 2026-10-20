# Allura Cowork

Coordinate a task, choose a useful next step, and hand work between Claude Code and Codex with the context and evidence intact.

Cowork supplies the shared conversation menu and handoff workflow. Add Team RAM for software work or Team Durham for brand work when the task calls for it. The current runtime keeps ownership until a real handoff occurs.

## Install and start

In Claude Code:

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install allura-cowork@allura-ecosystem
```

For Codex, follow the catalog's [installation guidance](../README.md#codex) and verify the package is available in your session.

Give a task directly, or say **“Help me choose the next step.”** On activation or a menu request, Cowork offers Next steps, Help with a prompt, Council, Work, Loop, Validate, and More. Clear tasks proceed without a compulsory menu.

For example:

> Prepare a handoff for this task. Include the goal, files changed, decisions, checks actually run, remaining risks, and next action.

## What it provides

| Workflow | Result |
|---|---|
| `cowork-start` | Project and memory context, a route, and an accountable owner |
| `cowork-handoff` | A structured packet for the receiving runtime |
| `cowork-validate` | A check of claims against evidence |
| `cowork-close` | An outcome summary and remaining risk |

Command registration varies by host; Codex discovers workflows through skills. The [handoff schema](schemas/handoff.schema.json), [golden examples](examples/golden/), and [failure examples](examples/failure/) show the required evidence.

Cowork instructs agents to distinguish a proposed action from an executed action. A named perspective, a loaded role, or a written handoff does not establish that another agent or runtime ran. These are workflow instructions, not a guarantee against unsupported claims.

## Memory and authority

Allura Brain supports scoped context retrieval and concise outcome logging. Use the authorized project scope; `allura-system` is the default only where that scope is authorized. If Brain is unavailable, report it and keep memory claims unconfirmed.

[Adaptive cowork](docs/ADAPTIVE-WORK.md) sets routes by risk, reuses fresh context, and preserves the configured model. Existing user authorization applies within its scope; protected actions and semantic promotion retain their approval boundaries.

## Package Contract

### Runtime manifests

Version `0.4.0` is published at `allura-cowork/` with `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json`. Its marketplace identity is `allura-cowork@allura-ecosystem`.

### Validation

From the catalog root:

```bash
python3 allura-cowork/scripts/validate_plugin.py allura-cowork
python3 allura-cowork/scripts/run_evals.py allura-cowork
python3 scripts/validate_manifests.py
```

Validate a handoff with `python3 allura-cowork/scripts/validate_handoff.py <packet.json>`. Offline cases in `evals/cases.json` check instruction contracts. They do not measure model performance or prove a live handoff.

### Dependencies and degraded behavior

A compatible Claude Code or Codex plugin environment is required. Python 3 enables the optional `UserPromptSubmit` context hook; without it, the hook silently does nothing. Memory-dependent work requires an authorized Allura Brain connection. Missing connections and unrun checks must be stated before claiming completion.
