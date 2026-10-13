from __future__ import annotations

import importlib.util
import json
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


def test_codex_marketplace_lists_every_portable_plugin():
    marketplace = json.loads(
        (ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8")
    )

    assert [entry["name"] for entry in marketplace["plugins"]] == [
        "allura-cowork",
        "team-durham",
        "team-ram-coding",
        "bumblebee",
    ]


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


def test_codex_rejects_claude_fields_before_distribution():
    validator = load_validator()
    errors = []
    validator.check_codex_contract({"commands": [], "agents": [], "mcp": "./.mcp.json", "skills": "./.opencode/skills/"}, "fixture", errors)
    assert any("unsupported field commands" in error for error in errors)
    assert any("unsupported field agents" in error for error in errors)
    assert any("unsupported field mcp" in error for error in errors)
    assert any("plugin-root skills" in error for error in errors)
    assert any("defaultPrompt" in error for error in errors)


def test_codex_marketplace_rejects_manifest_alias_mismatch(tmp_path, monkeypatch):
    validator = load_validator()
    monkeypatch.setattr(validator, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(validator, "PLUGINS", ["public-name"])
    marketplace = tmp_path / validator.CODEX_MARKETPLACE
    marketplace.parent.mkdir(parents=True)
    marketplace.write_text(json.dumps({"plugins": [{"name": "public-name", "source": {"source": "local", "path": "./plugin"}, "category": "Coding"}]}))
    manifest = tmp_path / "plugin/.codex-plugin/plugin.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"name": "source-name"}))
    errors = []
    validator.check_codex_marketplace(errors, [])
    assert any("manifest name must match marketplace alias" in error for error in errors)
    manifest.write_text(json.dumps({"name": "public-name"}))
    errors = []
    validator.check_codex_marketplace(errors, [])
    assert errors == []
