# CorpLawyer Bot

Corporate law and small-business tool planning instructions supplied by the owner.

The source skill is preserved byte-for-byte. Packaging supplies instructions, not a hosted legal database, legal research service, or automatic update mechanism. Current legal questions still require authoritative current sources and qualified review as appropriate.

## Package Contract

### Runtime manifests

Version `0.8.1`. Hermes uses `plugin.yaml` and `__init__.py`; Claude uses
`.claude-plugin/plugin.json` and discovers `skills/`. This package does not
install a model, start agents, add browser access, or configure credentials.

### Use

These packages are on `codex/hermes-plugin-setup-20261018`; default `main`
does not contain this release yet. Clone the release branch first:

```sh
git clone --branch codex/hermes-plugin-setup-20261018 --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
claude --plugin-dir ./plugins/corplawyer-bot
hermes plugins install "file://$(pwd)#plugins/corplawyer-bot" --enable
```

The native Hermes installer reads the committed local Git checkout. Select the
intended Hermes profile before installing. To load explicitly,
call `skill_view(name="corplawyer-bot:instructions")`, then give the task in ordinary chat.
Claude can select the skill as `/corplawyer-bot:instructions` after loading the package.

### Validation

Run `python3 scripts/validate_manifests.py` and
`python3 -m pytest tests/test_skill_packages.py` from the catalog root.
Use `claude plugin validate ./plugins/corplawyer-bot` for native Claude validation.
The registration tests also exercise native Hermes when its SDK is installed.

### Dependencies and degraded behavior

Instructions are bundled; live external services and runtime tools are not.
Report missing tools or authentication and limit claims to observed evidence.
Read `SOURCE_PROVENANCE.json` for the source version, content hashes, and changes.
This source package is distinct from the owner's existing account plugin;
publishing this repository does not update that account installation.
