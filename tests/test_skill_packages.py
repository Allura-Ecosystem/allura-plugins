"""Portable source integrity and isolated native skill registration checks."""
import hashlib
import importlib.util
import json
from pathlib import Path
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["prompt-optimization-bot", "corplawyer-bot", "team-durham-app-audit"]


@pytest.mark.parametrize("name", PACKAGES)
def test_skill_source_provenance_and_registration(name):
    root = ROOT / "plugins" / name
    receipt = json.loads((root / "SOURCE_PROVENANCE.json").read_text())
    skill = root / receipt["packagedFile"]
    digest = hashlib.sha256(skill.read_bytes()).hexdigest()
    assert digest == receipt["packagedSha256"]
    if name != "team-durham-app-audit":
        assert receipt["sourcePreserved"] is True
        assert digest == receipt["sourceSha256"]
    else:
        assert receipt["sourcePreserved"] is False
        text = skill.read_text()
        for required in ("STP before pixels", "allura-team-durham", "Munari audits read-only", "Rand tests UX read-only", "Glaser prepares visual fixes", "Kotler owns evidence"):
            assert required in text
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), root / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []
    module.register(types.SimpleNamespace(register_skill=lambda *args: calls.append(args)))
    assert len(calls) == 1
    assert calls[0][1] == skill
    assert skill.is_file()


@pytest.mark.parametrize("name", PACKAGES)
def test_native_hermes_registration(name, tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    plugins = pytest.importorskip("hermes_cli.plugins")
    root = ROOT / "plugins" / name
    spec = importlib.util.spec_from_file_location("native_" + name.replace("-", "_"), root / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manager = plugins.PluginManager()
    ctx = plugins.PluginContext(plugins.PluginManifest(name=name, path=str(root)), manager)
    module.register(ctx)
    skill_name = "app-audit" if name == "team-durham-app-audit" else "instructions"
    assert manager._plugin_skills[f"{name}:{skill_name}"]["path"].is_file()
    assert len(manager._plugin_skills) == 1
