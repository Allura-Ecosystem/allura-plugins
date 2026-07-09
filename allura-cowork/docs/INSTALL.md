# Install Allura Cowork

This install is local-first. It does not mutate runtime services, databases,
MCP config, cron, production, semantic memory, or Notion.

## Prerequisites

- Python 3
- `jq`
- A local clone containing `plugins/allura-cowork/`
- Claude Code and/or Codex configured to read local plugins

## Install For Codex

Copy the package to the local plugin directory:

```bash
mkdir -p ~/plugins
rsync -a plugins/allura-cowork/ ~/plugins/allura-cowork/
```

Register it in the Codex marketplace if your environment uses
`~/.agents/plugins/marketplace.json`:

```json
{
  "name": "allura-cowork",
  "source": {
    "source": "local",
    "path": "./plugins/allura-cowork"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Coding"
}
```

## Install For Claude

Copy the same package to Claude's plugin directory:

```bash
mkdir -p ~/.claude/plugins
rsync -a plugins/allura-cowork/ ~/.claude/plugins/allura-cowork/
```

Claude should see:

- `.claude-plugin/plugin.json`
- `skills/allura-cowork/SKILL.md`
- `agents/cowork-orchestrator.md`
- `commands/*.md`
- `hooks/hooks.json`

## Verify

Run these from the repo root:

```bash
python3 plugins/allura-cowork/scripts/validate_plugin.py plugins/allura-cowork
python3 plugins/allura-cowork/scripts/run_evals.py plugins/allura-cowork
printf '%s' '{"prompt":"Create a Claude and Codex cowork handoff"}' \
  | plugins/allura-cowork/hooks/cowork-context.py
```

Expected result: validation passes, evals pass, and the hook prints an Allura
Cowork reminder.
