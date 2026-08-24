# Catalog Contract Normalization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each current Allura catalog package independently verifiable without moving its public path.

**Architecture:** Keep `allura-plugins/` as the release-control root. Extend the existing Python manifest validator with one declarative package-contract registry; portable Claude/Codex packages and the Hermes-native provider use distinct contract variants. Package-local metadata and README sections supply the declared contract; repository tests verify the validator's behavior.

**Tech Stack:** Python 3 standard library, pytest, JSON, YAML-like Hermes manifest parsing, Markdown documentation.

**Spec:** `docs/superpowers/specs/2026-08-24-catalog-contract-normalization-design.md`

## Global Constraints

- Preserve existing package directories and public marketplace sources.
- Do not add a `packages/` subtree or split repositories.
- Hermes remains a provider variant and is not forced into Claude/Codex metadata.
- A missing optional integration must not prevent package discovery or validation.
- Package versions must agree across release metadata or explicitly state why they differ.
- No hard-coded absolute paths, secrets, or undocumented cross-package dependencies.

---

## File Structure

- `scripts/validate_manifests.py` — declarative package-contract registry and validation functions.
- `tests/test_validate_manifests.py` — unit and end-to-end validator coverage.
- `allura-cowork/package.json`, `team-durham/package.json`, `team-ram-coding/package.json` — version parity with public manifests.
- `allura-cowork/README.md`, `team-durham/README.md`, `team-ram-coding/README.md` — package-local contract and graceful-degradation statements.
- `plugins/hermes-allura-brain/README.md`, `plugins/hermes-allura-brain/plugin.yaml` — provider contract and version parity.
- `allura/README.md` — explicit internal-support disposition.
- `README.md`, `docs/DESIGN-PLUGIN-CATALOG.md`, `docs/REQUIREMENTS-MATRIX.md` — catalog evidence and traceability.

### Task 1: Add the machine-checkable package contract

**Files:**
- Modify: `scripts/validate_manifests.py`
- Modify: `tests/test_validate_manifests.py`

**Interfaces:**
- Produces `PACKAGE_CONTRACTS: dict[str, dict[str, object]]`, keyed by package path.
- Produces `check_package_contracts(errors: list[str], warnings: list[str]) -> None`.
- Consumes the existing `REPO_ROOT`, `parse_json`, `hard_fail`, and `HERMES_PLUGIN_MANIFEST` helpers.

- [ ] **Step 1: Write failing contract tests**

```python
def test_catalog_contracts_validate_current_packages(capsys):
    validator = load_validator()
    errors: list[str] = []
    warnings: list[str] = []
    validator.check_package_contracts(errors, warnings)
    assert errors == []


def test_contract_rejects_missing_required_readme(monkeypatch):
    validator = load_validator()
    monkeypatch.setitem(
        validator.PACKAGE_CONTRACTS["allura-cowork"], "readme", "missing.md"
    )
    errors: list[str] = []
    validator.check_package_contracts(errors, [])
    assert any("missing.md" in error for error in errors)
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `pytest tests/test_validate_manifests.py -q`

Expected: FAIL because `check_package_contracts` and `PACKAGE_CONTRACTS` do not exist.

- [ ] **Step 3: Implement the smallest contract registry and validator**

```python
PACKAGE_CONTRACTS = {
    "allura-cowork": {"kind": "portable", "readme": "README.md"},
    "team-durham": {"kind": "portable", "readme": "README.md"},
    "team-ram-coding": {"kind": "portable", "readme": "README.md"},
    "plugins/hermes-allura-brain": {"kind": "provider", "readme": "README.md"},
}


def check_package_contracts(errors: list[str], warnings: list[str]) -> None:
    for package, contract in PACKAGE_CONTRACTS.items():
        package_dir = REPO_ROOT / package
        readme = package_dir / str(contract["readme"])
        if not readme.is_file():
            hard_fail("CONTRACT", f"{package} missing {readme.name}", errors)
```

Extend this function to verify the required runtime manifest(s), package version parity, and a package-local `## Package Contract` README heading. Call it from `main()` after the existing Hermes check.

- [ ] **Step 4: Run focused and full validation**

Run: `pytest tests/test_validate_manifests.py -q && python3 scripts/validate_manifests.py`

Expected: PASS; output includes a contract-success line for each governed package.

- [ ] **Step 5: Commit**

```bash
git add scripts/validate_manifests.py tests/test_validate_manifests.py
```

### Task 2: Normalize the three portable package contracts

**Files:**
- Modify: `allura-cowork/package.json`, `allura-cowork/README.md`
- Modify: `team-durham/package.json`, `team-durham/README.md`
- Modify: `team-ram-coding/package.json`, `team-ram-coding/README.md`
- Test: `tests/test_validate_manifests.py`

**Interfaces:**
- Consumes portable-contract requirements from Task 1.
- Produces `package.json.version == "0.2.0"` and a `## Package Contract` section in every portable package README.

- [ ] **Step 1: Add a failing portable-contract assertion**

```python
def test_portable_package_versions_match_marketplace():
    validator = load_validator()
    errors: list[str] = []
    validator.check_package_contracts(errors, [])
    assert errors == []
```

- [ ] **Step 2: Run the focused test and verify version/README failures**

Run: `pytest tests/test_validate_manifests.py::test_portable_package_versions_match_marketplace -q`

Expected: FAIL, reporting the current `0.1.0` package versions and absent contract headings.

- [ ] **Step 3: Make portable metadata and README contracts explicit**

Set the three `package.json` version fields to `0.2.0`. Add a `## Package Contract` section to each README that names: supported runtime manifests, package-local commands/skills/agents, optional dependencies, visible degradation behavior, and the current installation path.

- [ ] **Step 4: Run validation**

Run: `pytest tests/test_validate_manifests.py -q && python3 scripts/validate_manifests.py`

Expected: PASS; marketplace, portable manifests, package versions, README contracts, and existing path checks remain valid.

- [ ] **Step 5: Commit**

```bash
git add allura-cowork team-durham team-ram-coding tests/test_validate_manifests.py
```

### Task 3: Normalize Hermes and classify internal support

**Files:**
- Modify: `plugins/hermes-allura-brain/README.md`
- Modify: `plugins/hermes-allura-brain/plugin.yaml`
- Modify: `allura/README.md`
- Modify: `scripts/validate_manifests.py`
- Modify: `tests/test_hermes_allura_brain.py`

**Interfaces:**
- Hermes consumes its native `plugin.yaml` and produces a provider-specific contract result.
- `allura/` produces an explicit `internal support; not marketplace-releasable` declaration rather than portable-package metadata.

- [ ] **Step 1: Write failing provider and internal-support tests**

```python
def test_hermes_provider_contract_is_checked(capsys):
    validator = load_validator()
    assert validator.main() == 0
    assert "CONTRACT OK: plugins/hermes-allura-brain (provider)" in capsys.readouterr().out
```

- [ ] **Step 2: Run focused tests and verify failure**

Run: `pytest tests/test_validate_manifests.py tests/test_hermes_allura_brain.py -q`

Expected: FAIL until the provider contract output and README section exist.

- [ ] **Step 3: Implement explicit provider and internal-support documentation**

Add the same `## Package Contract` heading to the Hermes README, but describe its native manifest, Hermes configuration path, secret scope, and failure behavior. Keep `plugin.yaml` at version `0.2.0`. State in `allura/README.md` that it is internal Codex support and excluded from marketplace validation until its placeholder manifest fields are completed. Do not add `allura/` to the public marketplace.

- [ ] **Step 4: Run all repository checks**

Run: `pytest -q && python3 scripts/validate_manifests.py && git diff --check`

Expected: PASS with no whitespace errors; Hermes behavior tests and all catalog checks remain green.

- [ ] **Step 5: Commit**

```bash
git add plugins/hermes-allura-brain allura scripts/validate_manifests.py tests
```

### Task 4: Repair catalog evidence and release drift

**Files:**
- Modify: `README.md`
- Modify: `docs/DESIGN-PLUGIN-CATALOG.md`
- Modify: `docs/REQUIREMENTS-MATRIX.md`
- Test: `tests/test_validate_manifests.py`

**Interfaces:**
- Consumes validator results and normalized package metadata.
- Produces documentation whose package count, command count, paths, versions, and internal/public classification agree with the repository.

- [ ] **Step 1: Write a failing documentation-evidence assertion**

```python
def test_readme_declares_current_portable_package_versions():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "package.json files are `0.2.0`" in text
```

- [ ] **Step 2: Run the assertion and verify failure**

Run: `pytest tests/test_validate_manifests.py::test_readme_declares_current_portable_package_versions -q`

Expected: FAIL because README currently describes `0.1.0` package metadata.

- [ ] **Step 3: Update catalog truth**

Replace stale version-parity wording, retain the documented 35 Team RAM command count, record Hermes as a provider variant, and add traceability entries for AD-005 and its package-contract acceptance criteria. Do not invent package installation proof for runtimes not verified by their native tools.

- [ ] **Step 4: Run release evidence checks**

Run: `pytest -q && python3 scripts/validate_manifests.py && git diff --check`

Expected: PASS; documentation agrees with normalized metadata and validation evidence.

- [ ] **Step 5: Commit**

```bash
git add README.md docs tests/test_validate_manifests.py
```

## Final Verification

- [ ] Run `pytest -q`.
- [ ] Run `python3 scripts/validate_manifests.py`.
- [ ] Run `git diff --check`.
- [ ] Verify all marketplace sources are unchanged and still resolve.
- [ ] Verify no package directory moved and no new `packages/` subtree exists.
- [ ] Request Pike review for public package contract simplicity and Fowler review for validator maintainability before merge.
