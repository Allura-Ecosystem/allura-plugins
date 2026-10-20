# Team Durham App Audit

Check a live website or app against its approved brand rules and report specific fixes.

Use this skill after brand strategy and `brand-truth.json` are locked. It compares observed color, typography, logo use, voice, and key user paths with the approved reference. The audit is read-only on the live application.

## What to provide

- The brand slug used under `clients/`.
- The target URL for live capture.
- Locked brand truth at `clients/{brand}/*brand-truth.json`.

A missing brand truth blocks the audit. An unavailable browser limits what can be observed; report that limit instead of claiming a live check.

## Install and use

In Claude Code:

```text
/plugin marketplace add Allura-Ecosystem/allura-plugins
/plugin install team-durham-app-audit@allura-ecosystem
/team-durham-app-audit:app-audit
```

For a local Claude session or Hermes installation:

```sh
git clone --branch main --single-branch https://github.com/Allura-Ecosystem/allura-plugins.git allura-plugin-release
cd allura-plugin-release
```

Choose your runtime:

```sh
# Claude: load the local package for this session
claude --plugin-dir ./plugins/team-durham-app-audit

# Hermes: install into the selected profile
hermes plugins install "file://$(pwd)#plugins/team-durham-app-audit" --enable
```

Hermes reads the committed checkout. Select the intended profile before installing, then load `skill_view(name="team-durham-app-audit:app-audit")`.

Say **“audit {brand}”**, **“ux test {brand}”**, or **“check compliance {brand}”**, with the target URL. Here, compliance means conformity with the locked brand rules; it does not establish legal or regulatory compliance.

## What the audit returns

Findings are ranked by severity, linked to captured evidence, and paired with specific proposed fixes. Reports and captures are saved under `clients/{brand}/audits/`. Applying fixes requires a separately authorized implementation task.

Munari owns brand review, Rand owns UX review, Glaser prepares visual fixes, and Kotler owns evidence. These are responsibilities; the report must say which agents actually ran.

## Package Contract

### Runtime manifests

Version `1.0.1` uses `plugin.yaml` and `__init__.py` for Hermes and `.claude-plugin/plugin.json` with `skills/` discovery for Claude. It does not install a browser, model, agents, or credentials.

### Validation

From the catalog root:

```sh
python3 scripts/validate_manifests.py
python3 -m pytest tests/test_skill_packages.py
claude plugin validate ./plugins/team-durham-app-audit
```

Registration tests include native Hermes cases when its SDK is installed. They do not prove that a live site was audited.

### Dependencies and degraded behavior

Live capture needs an available browser tool. Optional Allura evidence logging needs authenticated access to `allura-team-durham`. Denied access never authorizes switching credentials or tenants. Report only evidence actually observed; memory persistence requires a successful write receipt. Semantic promotion remains subject to human review.

[SOURCE_PROVENANCE.json](SOURCE_PROVENANCE.json) records source versions, hashes, and corrections. Publishing this Git-owned package does not update the owner's separate account plugin.
