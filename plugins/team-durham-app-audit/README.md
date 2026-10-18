# Team Durham App Audit

Read-only brand and UX audit against locked brand truth with scoped evidence.

Triggers: audit {brand}, ux test {brand}, check compliance {brand}. STP and locked brand truth precede capture. QA is read-only; tenant allura-team-durham. Source corrections are enumerated in SOURCE_PROVENANCE.json.

## Package Contract

### Runtime manifests

Version `1.0.1`. Hermes uses `plugin.yaml` and `__init__.py`; Claude uses
`.claude-plugin/plugin.json` and discovers `skills/`. This package does not
install a model, start agents, add browser access, or configure credentials.

### Use

These packages are on `codex/hermes-plugin-setup-20261018`; default `main`
does not contain this release yet. Clone the release branch first:

```sh
git clone --branch codex/hermes-plugin-setup-20261018 --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
claude --plugin-dir ./plugins/team-durham-app-audit
hermes plugins install "file://$(pwd)#plugins/team-durham-app-audit" --enable
```

The native Hermes installer reads the committed local Git checkout. Select the
intended Hermes profile before installing. To load explicitly,
call `skill_view(name="team-durham-app-audit:app-audit")`, then give the task in ordinary chat.
Claude can select the skill as `/team-durham-app-audit:app-audit` after loading the package.

### Validation

Run `python3 scripts/validate_manifests.py` and
`python3 -m pytest tests/test_skill_packages.py` from the catalog root.
Use `claude plugin validate ./plugins/team-durham-app-audit` for native Claude validation.
The registration tests also exercise native Hermes when its SDK is installed.

### Dependencies and degraded behavior

Instructions are bundled; live external services and runtime tools are not.
Report missing tools or authentication and limit claims to observed evidence.
Read `SOURCE_PROVENANCE.json` for the source version, content hashes, and changes.
This source package is distinct from the owner's existing account plugin;
publishing this repository does not update that account installation.
