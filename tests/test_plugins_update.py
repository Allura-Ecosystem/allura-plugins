"""Source-first updater cannot mutate user runtimes and propagates audit failures."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import pytest

UPDATER = Path(__file__).resolve().parents[1] / "scripts" / "plugins-update-all.sh"


def catalog(tmp_path):
    root = tmp_path / "catalog"
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    shutil.copyfile(UPDATER, scripts / UPDATER.name)
    (root / "source-locks.json").write_text(json.dumps({"sources": [{"id": "ram", "aliases": ["team-ram-coding"]}]}))
    stub = '''import json, os, sys
from pathlib import Path
name = Path(__file__).name
print(json.dumps({"command":name, "args":sys.argv[1:]}))
if os.environ.get("FAIL_COMMAND") == name:
    raise SystemExit(1)
if name == "verify_source_exports.py" and "--sync" in sys.argv:
    (Path(__file__).parents[1] / "synced").write_text("repository-only")
'''
    for filename in ["verify_source_exports.py", "sync_catalog_metadata.py", "validate_manifests.py", "model-policy.py"]:
        (scripts / filename).write_text(stub)
    external = tmp_path / "installed-cache"
    external.mkdir()
    (external / "sentinel").write_text("must stay unchanged")
    return root


def run(root, *args, fail=None):
    env = dict(os.environ)
    if fail:
        env["FAIL_COMMAND"] = fail
    return subprocess.run(["bash", str(root / "scripts" / UPDATER.name), *args], text=True, capture_output=True, env=env)


def snapshot(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def commands(outcome):
    return [json.loads(line) for line in outcome.stdout.splitlines() if line.startswith("{")]


@pytest.mark.parametrize("args", [[], ["--dry-run"], ["--dry-run", "--package", "ram"]])
def test_default_and_dry_run_are_read_only_without_upstream_fetch(tmp_path, args):
    root = catalog(tmp_path)
    before = snapshot(tmp_path)
    outcome = run(root, *args)
    assert outcome.returncode == 0, outcome.stderr
    assert snapshot(tmp_path) == before
    assert [c["command"] for c in commands(outcome)] == ["sync_catalog_metadata.py", "validate_manifests.py", "model-policy.py"]
    assert commands(outcome)[0]["args"] == ["--check"]
    assert "not reverified" in outcome.stdout


def test_explicit_sources_and_package_filters_are_forwarded_literally(tmp_path):
    root = catalog(tmp_path)
    source = "ram=" + str(tmp_path / "source with spaces")
    before = snapshot(tmp_path)
    outcome = run(root, "--dry-run", "team-ram-coding", "--source", source)
    assert outcome.returncode == 0
    assert commands(outcome)[0] == {"command": "verify_source_exports.py", "args": ["--check", "--package", "team-ram-coding", "--source", source]}
    assert snapshot(tmp_path) == before


def test_sync_only_regenerates_repo_and_checks_result(tmp_path):
    root = catalog(tmp_path)
    before = snapshot(tmp_path / "installed-cache")
    outcome = run(root, "--sync", "--package=ram", "--source=ram=/local/source")
    assert outcome.returncode == 0
    assert (root / "synced").read_text() == "repository-only"
    rows = commands(outcome)
    assert rows[0]["args"] == ["--sync", "--package", "ram", "--source", "ram=/local/source"]
    assert rows[1] == {"command": "sync_catalog_metadata.py", "args": []}
    assert rows[-1]["args"] == ["--check", "--package", "ram", "--source", "ram=/local/source"]
    assert snapshot(tmp_path / "installed-cache") == before


@pytest.mark.parametrize("args", [["--runtime", "claude"], ["--install"], ["--package"], ["--source"], ["--sync", "--dry-run"], ["missing-package"]])
def test_invalid_options_fail_before_running_tools(tmp_path, args):
    root = catalog(tmp_path)
    before = snapshot(tmp_path)
    outcome = run(root, *args)
    assert outcome.returncode == 2
    assert commands(outcome) == []
    assert snapshot(tmp_path) == before


@pytest.mark.parametrize("failed", ["verify_source_exports.py", "sync_catalog_metadata.py", "validate_manifests.py", "model-policy.py"])
def test_failed_audit_never_reports_success(tmp_path, failed):
    root = catalog(tmp_path)
    outcome = run(root, "--dry-run", "--source", "ram=/local/source", fail=failed)
    assert outcome.returncode != 0
    assert "No changes made" not in outcome.stdout
    assert "audit passed" not in outcome.stdout


def test_audit_bindings_implicitly_select_only_local_sources(tmp_path):
    root = catalog(tmp_path)
    outcome = run(root, "--dry-run", "--source", "ram=/local/source")
    assert outcome.returncode == 0
    assert commands(outcome)[0]["args"] == ["--check", "--source", "ram=/local/source", "--package", "ram"]


def test_audit_cannot_fetch_an_unbound_selected_source(tmp_path):
    root = catalog(tmp_path)
    path = root / "source-locks.json"
    data = json.loads(path.read_text())
    data["sources"].append({"id": "durham", "aliases": []})
    path.write_text(json.dumps(data))
    before = snapshot(tmp_path)
    outcome = run(root, "--dry-run", "--package", "durham", "--source", "ram=/local/source")
    assert outcome.returncode == 2
    assert "requires --source" in outcome.stderr
    assert commands(outcome) == []
    assert snapshot(tmp_path) == before
