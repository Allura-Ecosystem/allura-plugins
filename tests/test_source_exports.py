"""Regression checks for pinned local exports and changing source allowlists."""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


def module(name):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def git(path, *args):
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def test_local_export_uses_pinned_commit_not_dirty_worktree(tmp_path):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q")
    git(source, "config", "user.name", "Export Test")
    git(source, "config", "user.email", "export@example.test")
    git(source, "remote", "add", "origin", "https://github.com/Allura-Ecosystem/example.git")
    (source / "value.txt").write_text("committed")
    git(source, "add", "value.txt")
    git(source, "commit", "-qm", "fixture")
    revision = git(source, "rev-parse", "HEAD")
    (source / "value.txt").write_text("uncommitted")
    (source / "private.txt").write_text("do not export")
    lock = {"id": "example", "repository": "https://github.com/Allura-Ecosystem/example.git", "commit": revision}
    checkout = exports.clone_pinned(lock, tmp_path / "clones", source)
    assert (checkout / "value.txt").read_text() == "committed"
    assert not (checkout / "private.txt").exists()
    assert git(checkout, "status", "--porcelain") == ""
    lock["repository"] = "https://github.com/Allura-Ecosystem/another.git"
    with pytest.raises(exports.ExportError, match="origin differs"):
        exports.clone_pinned(lock, tmp_path / "other", source)


def test_package_export_excludes_non_allowlisted_files_and_detects_tampering(tmp_path):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    source.mkdir()
    (source / "README.md").write_text("public")
    (source / "private.txt").write_text("excluded")
    (source / "package.json").write_text(json.dumps({"files": ["README.md"]}))
    lock = {"id": "example", "manifest": "package.json", "exporter": "package-files", "repository": "https://github.com/Allura-Ecosystem/example.git", "commit": "a" * 40}
    output = tmp_path / "export"
    exports.generate_package_files(source, output, lock)
    assert not (output / "private.txt").exists()
    exports.verify_source_receipt(output, lock)
    (output / "README.md").write_text("tampered")
    with pytest.raises(exports.ExportError, match="inventory mismatch"):
        exports.verify_source_receipt(output, lock)


@pytest.mark.parametrize("path", ["../private", "/tmp/private"])
def test_package_export_rejects_escape(tmp_path, path):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    source.mkdir()
    (source / "package.json").write_text(json.dumps({"files": [path]}))
    with pytest.raises(exports.ExportError, match="unsafe"):
        exports.generate_package_files(source, tmp_path / "out", {"manifest": "package.json"})


def test_package_export_rejects_symlinks(tmp_path):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    source.mkdir()
    (source / "link").symlink_to(tmp_path)
    (source / "package.json").write_text(json.dumps({"files": ["link"]}))
    with pytest.raises(exports.ExportError, match="symlinked"):
        exports.generate_package_files(source, tmp_path / "out", {"manifest": "package.json"})


@pytest.mark.parametrize("relative", ["link/private.txt", "link/folder"])
def test_package_export_rejects_symlink_ancestors(tmp_path, relative):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    source.mkdir()
    external = tmp_path / "external"
    (external / "folder").mkdir(parents=True)
    (external / "private.txt").write_text("must not copy")
    (external / "folder/private.txt").write_text("must not copy")
    (source / "link").symlink_to(external, target_is_directory=True)
    (source / "package.json").write_text(json.dumps({"files": [relative]}))
    with pytest.raises(exports.ExportError, match="symlinked"):
        exports.generate_package_files(source, tmp_path / "out", {"manifest": "package.json"})


def test_mortgate_allowlist_count_comes_from_lock(tmp_path):
    exports = module("verify_source_exports")
    source = tmp_path / "source"
    payload = source / "microsoft-cowork"
    (payload / "appPackage").mkdir(parents=True)
    (payload / "appPackage/manifest.json").write_text(json.dumps({"version": "0.2.1"}))
    include = ["appPackage/manifest.json"]
    contract = {"packageId": "mortagate-cowork", "canonical": {"sourceRoot": "microsoft-cowork"}, "destination": {"path": "packages/mortagate-cowork"}, "export": {"include": include}}
    (source / "catalog-export.json").write_text(json.dumps(contract))
    lock = {"id": "mortagate-cowork", "manifest": "catalog-export.json", "sourceManifestName": "mortagate-cowork", "sourceRoot": "microsoft-cowork", "destination": "packages/mortagate-cowork", "runtimeVersion": "0.2.1", "runtime": "microsoft-cowork", "repository": "https://github.com/Allura-Ecosystem/mortagate.git", "commit": "a" * 40, "exportFileCount": 1}
    exports.generate_mortagate(source, tmp_path / "out", lock)
    exports.verify_source_receipt(tmp_path / "out", lock)
    lock["exportFileCount"] = 19
    with pytest.raises(exports.ExportError, match="allowlist size"):
        exports.generate_mortagate(source, tmp_path / "bad", lock)


def test_sync_allows_catalog_version_transition_but_checks_source_version(tmp_path):
    exports = module("verify_source_exports")
    for relative in ["package.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"name": "example", "version": "0.2.0"}))
    lock = {"id": "example", "marketplace": True, "marketplaceAlias": "example", "destination": "example", "runtimeVersion": "0.2.0", "packageVersion": "0.2.0", "sourceManifestName": "example", "sourcePackageName": "example"}
    catalog = {"plugins": [{"name": "example", "source": "./example", "version": "0.1.0"}]}
    with pytest.raises(exports.ExportError, match="marketplace/runtime"):
        exports.validate_versions(tmp_path, lock, catalog)
    exports.validate_versions(tmp_path, lock, catalog, syncing=True)
    (tmp_path / ".codex-plugin/plugin.json").write_text(json.dumps({"name": "example", "version": "wrong"}))
    with pytest.raises(exports.ExportError, match="runtime version parity"):
        exports.validate_versions(tmp_path, lock, catalog, syncing=True)


def test_runtime_identity_allows_source_owned_codex_name_but_rejects_alias_drift(tmp_path):
    exports = module("verify_source_exports")
    for relative, name in [("package.json", "@example/source"), (".claude-plugin/plugin.json", "source-name"), (".codex-plugin/plugin.json", "public-name")]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"name": name, "version": "0.2.0"}))
    lock = {"id": "example", "marketplace": True, "marketplaceAlias": "public-name", "destination": "example", "runtimeVersion": "0.2.0", "packageVersion": "0.2.0", "sourceManifestName": "source-name", "codexManifestName": "public-name", "sourcePackageName": "@example/source"}
    catalog = {"plugins": [{"name": "public-name", "source": "./example", "version": "0.2.0"}]}
    exports.validate_versions(tmp_path, lock, catalog)
    (tmp_path / ".codex-plugin/plugin.json").write_text(json.dumps({"name": "source-name", "version": "0.2.0"}))
    with pytest.raises(exports.ExportError, match="identity mismatch"):
        exports.validate_versions(tmp_path, lock, catalog)
    lock["codexManifestName"] = "source-name"
    with pytest.raises(exports.ExportError, match="Codex manifest name must match marketplace alias"):
        exports.validate_versions(tmp_path, lock, catalog)
