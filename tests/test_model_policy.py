"""Model policy audits are read-only; benchmark plans are never measurements."""
import hashlib
import json
from pathlib import Path
import subprocess

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "model-policy.py"


def run(*args):
    return subprocess.run(["/usr/bin/python3", str(SCRIPT), *map(str, args)], capture_output=True, text=True)


def fixture(root):
    plugin = root / "team-ram-coding"
    plugin.mkdir()
    (plugin / "SOURCE.json").write_text('{"canonical":false}')
    for directory, filename, content in [
        ("agents", "woz.md", "---\nname: woz\nmodel: inherit\n---\nmodel: ignored body text\n"),
        (".opencode/agent/core", "woz.md", "---\nname: woz\n---\nModel omitted.\n"),
        (".codex/agents", "woz.toml", 'name = "woz"\n'),
    ]:
        path = plugin / directory / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return plugin


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def test_audit_never_mutates_and_accepts_inheritance(tmp_path):
    fixture(tmp_path)
    before = snapshot(tmp_path)
    for flags in [[], ["--dry-run"], ["--runtime", "claude", "woz"]]:
        outcome = run("audit", "--root", tmp_path, *flags)
        assert outcome.returncode == 0, outcome.stderr
        assert json.loads(outcome.stdout)["status"] == "passed"
        assert snapshot(tmp_path) == before


@pytest.mark.parametrize("runtime,path,content", [
    ("claude", "agents/woz.md", "---\nmodel: pinned-unverified\n---\n"),
    ("opencode", ".opencode/agent/core/woz.md", "---\nmodel: inherit\n---\n"),
    ("codex", ".codex/agents/woz.toml", 'name = "woz"\nmodel = "pinned-unverified"\n'),
])
def test_drift_is_reported_without_rewriting(tmp_path, runtime, path, content):
    plugin = fixture(tmp_path)
    (plugin / path).write_text(content)
    before = snapshot(tmp_path)
    outcome = run("audit", "--root", tmp_path, "--runtime", runtime)
    assert outcome.returncode == 1
    assert json.loads(outcome.stdout)["drift"] == 1
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("args", [
    ["audit", "--runtime", "unsupported"], ["audit", "--runtime"],
    ["audit", "--bad-option"], ["eval", "--compare", "last"],
    ["performance", "--days", "7"], ["performance", "--suggest"],
])
def test_unsupported_or_missing_options_fail(args):
    assert run(*args).returncode == 2


def test_no_matching_agent_is_not_a_pass(tmp_path):
    fixture(tmp_path)
    outcome = run("audit", "--root", tmp_path, "--agent", "missing")
    assert outcome.returncode == 2
    assert "no matching" in outcome.stderr


@pytest.mark.parametrize("operation", ["eval", "performance"])
def test_no_measurements_is_not_a_successful_evaluation(tmp_path, operation):
    before = snapshot(tmp_path)
    outcome = run(operation, "--root", tmp_path)
    assert outcome.returncode == 2
    report = json.loads(outcome.stdout)
    assert report["status"] == "not-run"
    assert report["measurements"] is None
    plan = run(operation, "--root", tmp_path, "--dry-run", "--runtime", "claude", "woz")
    assert plan.returncode == 0
    assert json.loads(plan.stdout)["status"] == "not-run"
    assert snapshot(tmp_path) == before


def test_agent_symlink_cannot_escape_selected_catalog(tmp_path):
    root = tmp_path / "catalog"
    root.mkdir()
    plugin = fixture(root)
    external = tmp_path / "external.md"
    external.write_text("---\nmodel: inherit\n---\n")
    (plugin / "agents" / "escape.md").symlink_to(external)
    outcome = run("audit", "--root", root)
    assert outcome.returncode == 2
    assert "escapes catalog" in outcome.stderr
