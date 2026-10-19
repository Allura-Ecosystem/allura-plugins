# CorpLawyer Bot

Six practical skills support business issue discovery, contract review through a
counsel brief, current official-source research, and authorized Allura continuity.
The original owner prompt is retained under `provenance/`; it is no longer the
active instruction to design a tool for every request.

## Package contract

Version `0.9.0`. Native Hermes registers each actual `SKILL.md` file under the
`corplawyer-bot:` namespace. Claude discovers the six folders under `./skills/`.
No browser service, legal database, model, credentials or memory provider is
installed by this package. Broader compliance automation remains later work.

## Use

The source release is on `codex/hermes-plugin-setup-20261018`:

```sh
git clone --branch codex/hermes-plugin-setup-20261018 --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
claude --plugin-dir ./plugins/corplawyer-bot
hermes plugins install "file://$(pwd)#plugins/corplawyer-bot" --enable
```

The Hermes installer reads the committed checkout. Select the intended Hermes
profile before installing. Load the entry with
`skill_view(name="corplawyer-bot:instructions")` and state the task in chat.
For a direct review use `skill_view(name="corplawyer-bot:contract-review")`.
Claude exposes `/corplawyer-bot:instructions` and
`/corplawyer-bot:contract-review`; the other folders are discoverable in the same
namespace. Ordinary clear tasks proceed without a compulsory menu.

The bundled skills are `instructions`, `matter-intake`, `legal-research`,
`contract-review`, `counsel-brief`, and `allura-continuity`. Each links to the
related workflow only when needed. A contract review starts when requested or
relevant to the owner's issue. Unclear business help starts with issue discovery.

## Dependencies and limits

Current legal claims require actual retrieval of current official sources.
Without an available research tool the agent can examine supplied clauses and
prepare a draft brief, explicitly leaving legal conclusions unverified.
Allura continuity uses only the existing authenticated provider and authorized
business/matter scope. Missing or denied memory never triggers another tenant,
identity or credential. Document-only work may continue from supplied material
with the limitation stated. Concise permitted outcome retention is separate from
bulk agreement retention, and semantic promotion remains human governed.

Prompt Bot and Allura Council are optional installed capabilities, not hidden
package dependencies. No skill may claim they executed without actual tools.
Publishing this source does not update the owner's account plugin or caches.

## Validation and realistic sample

From the catalog root:

```sh
python3 scripts/validate_manifests.py
python3 -m pytest tests/test_skill_packages.py
claude plugin validate ./plugins/corplawyer-bot
```

Run pytest using the Hermes virtualenv interpreter to exercise its actual SDK;
without that SDK the native cases skip. Tests use a temporary `HERMES_HOME` and
do not call live legal or memory services. They verify source snapshot hashes,
all six registrations, namespace paths, and bundled-reference integrity.

`evaluation/fictional-services-agreement.md` is a fictional supplied-document
exercise. `evaluation/scenario.json` gives a request and capability restrictions;
`evaluation/review-criteria.md` records the observable evidence to assess.
These are fixtures, not an actual legal opinion, live source-research receipt,
Allura access result or behavioral evaluation. Native conversation evaluation
must record its actual response before anyone claims the workflow passed.

`SOURCE_PROVENANCE.json` records the unchanged original snapshot and hashes of
transformed/new skills. Changes here do not overwrite the source account plugin.
