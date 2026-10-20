# CorpLawyer Bot

Understand a business issue, review a supplied contract, and prepare a clear brief for counsel.

Six skills help organize the facts, inspect clauses, research current official sources when tools are available, and retain permitted context through Allura. An unclear request starts with issue discovery. A direct contract-review request goes straight to that workflow.

## Install and use

In Claude Code:

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install corplawyer-bot@allura-ecosystem
/corplawyer-bot:instructions
```

For a local Claude session or Hermes installation:

```sh
git clone --branch main --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
```

Choose your runtime:

```sh
# Claude: load the local package for this session
claude --plugin-dir ./plugins/corplawyer-bot

# Hermes: install into the selected profile
hermes plugins install "file://$(pwd)#plugins/corplawyer-bot" --enable
```

Hermes reads the committed checkout. Select the intended profile before installing, then load `skill_view(name="corplawyer-bot:instructions")`. For a direct review, load `skill_view(name="corplawyer-bot:contract-review")`. Claude exposes `/corplawyer-bot:contract-review` after installation.

For example:

> Review this services agreement from the customer's perspective. Link each finding to a clause, list missing information, and prepare questions for counsel. Distinguish document observations from legal conclusions that need current sources.

## Choose a skill

| Skill | Purpose |
|---|---|
| `instructions` | Choose the workflow that fits the request |
| `matter-intake` | Establish the issue, relevant facts, and missing information |
| `legal-research` | Research legal questions using current official sources |
| `contract-review` | Inspect supplied clauses and prepare proposed revisions |
| `counsel-brief` | Assemble facts, findings, and questions for counsel |
| `allura-continuity` | Retrieve or retain permitted context in an authorized matter scope |

Hermes names begin with `corplawyer-bot:`. Claude discovers the same six skill folders. Skills load related workflows only when needed; clear tasks do not require a menu.

## Dependencies and limits

Legal conclusions require actual retrieval of current official sources. Without a research tool, the agent can review supplied text and prepare a draft brief, leaving those conclusions unverified. This package does not supply a legal database or browser service.

Allura continuity uses an existing authenticated provider and authorized business or matter scope. Missing or denied access must be reported; it does not permit a change of tenant, identity, or credentials. Work from supplied documents can continue with that limitation stated. Permitted concise outcome retention is separate from retaining entire agreements. Semantic promotion requires human review.

Prompt Bot and Allura Council are optional installed capabilities. Their execution must be confirmed before being claimed. Broader compliance automation remains outside this release.

## Package contract

Version `0.9.0` uses `plugin.yaml` and `__init__.py` for Hermes and `.claude-plugin/plugin.json` for Claude. It installs no model, credentials, or memory provider. Publishing it does not update the owner's separate account GPT or runtime caches.

[SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json) records the original snapshot and the hashes of transformed and new skills. The original owner prompt is preserved in [`provenance/`](provenance/); its generic tool-design instructions are no longer the active workflow.

## Validation and sample review

From the catalog root:

```sh
python3 scripts/validate_manifests.py
python3 -m pytest tests/test_skill_packages.py
claude plugin validate ./plugins/corplawyer-bot
```

Use the Hermes virtualenv interpreter for its actual SDK cases; they skip when the SDK is absent. Tests use a temporary `HERMES_HOME` to check hashes, six registrations, namespace paths, and bundled references. They do not call live legal or memory services.

The [fictional services agreement](evaluation/fictional-services-agreement.md), [scenario](evaluation/scenario.json), and [review criteria](evaluation/review-criteria.md) provide a repeatable supplied-document exercise. They are fixtures, not a legal opinion or a successful runtime evaluation. A behavioral result requires the actual response and review evidence.
