"""Portable source integrity and isolated native skill registration checks."""
import hashlib
import importlib.util
import json
import re
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
    if name == "prompt-optimization-bot":
        assert receipt["sourcePreserved"] is True
        assert digest == receipt["sourceSha256"]
    elif name == "team-durham-app-audit":
        assert receipt["sourcePreserved"] is False
        text = skill.read_text()
        for required in ("STP before pixels", "allura-team-durham", "Munari audits read-only", "Rand tests UX read-only", "Glaser prepares visual fixes", "Kotler owns evidence"):
            assert required in text
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), root / "__init__.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    calls = []
    module.register(types.SimpleNamespace(register_skill=lambda *args: calls.append(args)))
    expected = {p.parent.name: p for p in (root / "skills").glob("*/SKILL.md")}
    assert dict(calls) == expected
    assert len(calls) == len(expected)
    assert calls[0][1] == skill
    assert all(path.is_file() for _, path in calls)


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
    expected = {
        f"{name}:{p.parent.name}": p
        for p in (root / "skills").glob("*/SKILL.md")
    }
    assert {
        key: value["path"] for key, value in manager._plugin_skills.items()
    } == expected
    assert all(path.is_file() for path in expected.values())


def test_corplawyer_original_snapshot_and_transformed_resources():
    root = ROOT / "plugins" / "corplawyer-bot"
    receipt = json.loads((root / "SOURCE_PROVENANCE.json").read_text())
    original = root / receipt["originalSnapshot"]
    assert hashlib.sha256(original.read_bytes()).hexdigest() == receipt["sourceSha256"]
    assert receipt["originalSnapshotSha256"] == receipt["sourceSha256"]
    assert receipt["sourcePreserved"] is False
    assert receipt["packagedSha256"] != receipt["sourceSha256"]
    resources = {item["path"]: item["sha256"] for item in receipt["resources"]}
    actual = {p.relative_to(root).as_posix() for p in (root / "skills").glob("*/SKILL.md")}
    assert set(resources) == actual
    assert len(actual) == 6
    for path, expected in resources.items():
        assert hashlib.sha256((root / path).read_bytes()).hexdigest() == expected


def test_corplawyer_bundled_references_resolve_within_package():
    root = (ROOT / "plugins" / "corplawyer-bot").resolve()
    for skill in (root / "skills").glob("*/SKILL.md"):
        for target in re.findall(r"\]\(([^)]+)\)", skill.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            resolved = (skill.parent / target.split("#")[0]).resolve()
            assert resolved.is_relative_to(root), (skill, target)
            assert resolved.is_file(), (skill, target)
