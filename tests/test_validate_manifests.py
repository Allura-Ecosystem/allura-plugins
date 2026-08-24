from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_manifests",
        ROOT / "scripts" / "validate_manifests.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_catalog_validation_includes_hermes_native_plugin(capsys):
    validator = load_validator()

    assert validator.main() == 0

    output = capsys.readouterr().out
    assert "HERMES MANIFEST OK: allura-brain v0.2.0" in output


def test_catalog_contracts_validate_current_packages():
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
