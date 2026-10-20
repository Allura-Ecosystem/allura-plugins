# Prompt Optimization Bot

Turn a rough request into a clear prompt while preserving what you want to accomplish.

Use it to name the deliverable, supply relevant context, resolve conflicting instructions, and define a useful result. The response is a prompt you can copy, with brief notes where they help. It does not execute that prompt unless you ask.

## Install and use

In Claude Code:

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install prompt-optimization-bot@allura-ecosystem
/prompt-optimization-bot:instructions
```

For a local Claude session or Hermes installation, clone the catalog's `main` branch:

```sh
git clone --branch main --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
```

Choose your runtime:

```sh
# Claude: load the local package for this session
claude --plugin-dir ./plugins/prompt-optimization-bot

# Hermes: install into the selected profile
hermes plugins install "file://$(pwd)#plugins/prompt-optimization-bot" --enable
```

Hermes reads the committed Git checkout. Select the intended profile before installing, then load `skill_view(name="prompt-optimization-bot:instructions")`.

Give your request in ordinary language:

> Improve this prompt for Team Durham: review our plugin README for clarity and consistent Allura branding. Keep the installation commands accurate and flag claims that need evidence.

## Optional prompt modes

| Mode | Use it to… |
|---|---|
| `/FORGE` | Build a prompt from an idea |
| `/REFINE` | Improve an existing prompt |
| `/ANALYSE` | Find weaknesses and suggest specific fixes |
| `/EXPLORE` | Compare different approaches |
| `/TEST` | Create test cases and a comparison rubric |
| `/QUICK` | Return only the optimized prompt |

These are prompt modes interpreted after the skill loads, not globally registered slash commands. `/TEST` prepares a way to evaluate prompts; it does not establish that testing ran.

## Package Contract

### Runtime manifests

Version `0.33.2` preserves the owner-supplied instruction skill byte-for-byte. Hermes uses `plugin.yaml` and `__init__.py`; Claude uses `.claude-plugin/plugin.json` and discovers `skills/`.

### Validation

From the catalog root:

```sh
python3 scripts/validate_manifests.py
python3 -m pytest tests/test_skill_packages.py
claude plugin validate ./plugins/prompt-optimization-bot
```

Registration tests include native Hermes cases when its SDK is installed.

### Dependencies and degraded behavior

The package supplies instructions. Tools, models, browser access, and credentials come from the runtime. Missing inputs remain questions or placeholders, and claims about testing need actual results.

[SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json) records source hashes and version. This Git-owned package is separate from the owner's account GPT; publishing it does not update that account installation.
