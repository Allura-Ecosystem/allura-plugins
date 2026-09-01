#!/usr/bin/env python3
"""Regenerate pinned standalone-source exports and check catalog drift."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCKS_PATH = ROOT / "source-locks.json"
MARKETPLACE_PATH = ROOT / ".claude-plugin/marketplace.json"
SECRET_PATTERNS = {
    "private key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "OpenAI/Anthropic token": re.compile(rb"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{16,}"),
    "Notion token": re.compile(rb"\bntn_[A-Za-z0-9]{10,}"),
    "GitHub token": re.compile(rb"\bgh[opsu]_[A-Za-z0-9]{20,}"),
}


class ExportError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExportError(f"cannot read JSON {path}: {exc}") from exc


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command: list[str], *, cwd: Path) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip()
        raise ExportError(f"command failed ({' '.join(command)}): {detail}")
    return result.stdout.strip()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_inventory(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for base, dirs, files in os.walk(root, followlinks=False):
        base_path = Path(base)
        for name in sorted(dirs):
            path = base_path / name
            if path.is_symlink():
                target = os.readlink(path)
                rows.append({
                    "path": path.relative_to(root).as_posix(),
                    "kind": "symlink",
                    "sha256": hashlib.sha256(target.encode()).hexdigest(),
                    "target": target,
                })
        dirs[:] = [name for name in dirs if not (base_path / name).is_symlink()]
        for name in sorted(files):
            path = base_path / name
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                target = os.readlink(path)
                rows.append({
                    "path": relative,
                    "kind": "symlink",
                    "sha256": hashlib.sha256(target.encode()).hexdigest(),
                    "target": target,
                })
            else:
                rows.append({
                    "path": relative,
                    "kind": "file",
                    "sha256": sha256_file(path),
                    "size": path.stat().st_size,
                })
    return sorted(rows, key=lambda row: row["path"])


def clone_pinned(lock: dict[str, Any], parent: Path) -> Path:
    parent.mkdir(parents=True, exist_ok=True)
    checkout = parent / lock["id"]
    run(["git", "clone", "--quiet", "--no-checkout", lock["repository"], str(checkout)], cwd=parent)
    commit = lock["commit"]
    try:
        run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=checkout)
    except ExportError:
        run(["git", "fetch", "--quiet", "origin", commit], cwd=checkout)
        run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=checkout)
    run(["git", "checkout", "--quiet", "--detach", commit], cwd=checkout)
    actual = run(["git", "rev-parse", "HEAD"], cwd=checkout)
    if actual != commit:
        raise ExportError(f"{lock['id']}: checkout resolved to {actual}, expected {commit}")
    if run(["git", "status", "--porcelain"], cwd=checkout):
        raise ExportError(f"{lock['id']}: pinned source checkout is unexpectedly dirty")
    return checkout


def validate_lock(lock: dict[str, Any]) -> None:
    required = {
        "id", "aliases", "repository", "commit", "manifest", "exporter", "destination",
        "runtime", "marketplace", "sourceManifestName", "sourcePackageName", "packageVersion", "runtimeVersion",
    }
    missing = sorted(required - lock.keys())
    if missing:
        raise ExportError(f"source lock {lock.get('id', '<unknown>')} missing: {', '.join(missing)}")
    if not re.fullmatch(r"[0-9a-f]{40}", lock["commit"]):
        raise ExportError(f"{lock['id']}: commit must be a full lowercase SHA")
    destination = Path(lock["destination"])
    if destination.is_absolute() or ".." in destination.parts:
        raise ExportError(f"{lock['id']}: destination escapes repository")


def generate_mortagate(source: Path, output: Path, lock: dict[str, Any]) -> None:
    contract_path = source / lock["manifest"]
    contract = read_json(contract_path)
    if contract.get("packageId") != lock["sourceManifestName"]:
        raise ExportError("mortagate contract packageId does not match lock")
    source_root = contract.get("canonical", {}).get("sourceRoot")
    if source_root != lock.get("sourceRoot"):
        raise ExportError("mortagate sourceRoot does not match lock")
    destination = contract.get("destination", {}).get("path")
    if destination != lock["destination"]:
        raise ExportError("mortagate contract destination does not match lock")
    include = contract.get("export", {}).get("include")
    if not isinstance(include, list) or len(include) != 19 or len(set(include)) != 19:
        raise ExportError("mortagate contract must contain the exact 19-file allowlist")
    output.mkdir(parents=True)
    payload_rows: list[dict[str, Any]] = []
    for relative in include:
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise ExportError(f"mortagate unsafe allowlist path: {relative}")
        source_file = source / source_root / relative_path
        if not source_file.is_file() or source_file.is_symlink():
            raise ExportError(f"mortagate allowlisted regular file missing: {relative}")
        target = output / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_file, target)
        payload_rows.append({"path": relative_path.as_posix(), "sha256": sha256_file(target), "size": target.stat().st_size})
    forbidden = contract.get("export", {}).get("forbiddenPatterns", [])
    for row in payload_rows:
        parts = Path(row["path"]).parts
        for pattern in forbidden:
            if any(fnmatch.fnmatch(part, pattern) for part in parts) or fnmatch.fnmatch(row["path"], pattern):
                raise ExportError(f"mortagate forbidden pattern {pattern!r} matched {row['path']}")
    manifest = read_json(output / "appPackage/manifest.json")
    if manifest.get("version") != lock["runtimeVersion"]:
        raise ExportError("mortagate Microsoft manifest version does not match lock")
    receipt = {
        "schemaVersion": 1,
        "generated": True,
        "authoritative": False,
        "manualEdits": "forbidden; change the standalone source and regenerate",
        "sourceRepository": lock["repository"],
        "sourceCommit": lock["commit"],
        "contractPath": lock["manifest"],
        "contractSha256": sha256_file(contract_path),
        "generatedBy": "allura-plugins/scripts/verify_source_exports.py",
        "packageId": lock["id"],
        "runtime": lock["runtime"],
        "version": lock["runtimeVersion"],
        "files": payload_rows,
    }
    write_json(output / "EXPORT_PROVENANCE.json", receipt)


def generate(lock: dict[str, Any], source: Path, output: Path) -> None:
    if lock["id"] == "team-ram":
        run(["node", lock["exporter"], str(output)], cwd=source)
    elif lock["id"] == "team-durham":
        run([sys.executable, lock["exporter"], "--output", str(output)], cwd=source)
    elif lock["id"] == "mortagate-cowork":
        generate_mortagate(source, output, lock)
    else:
        raise ExportError(f"unsupported source id: {lock['id']}")


def verify_no_secrets(output: Path, lock: dict[str, Any]) -> None:
    for row in tree_inventory(output):
        if row["kind"] != "file":
            continue
        path = output / row["path"]
        if path.stat().st_size > 8 * 1024 * 1024:
            continue
        data = path.read_bytes()
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                raise ExportError(f"{lock['id']}: secret-like {label} in {row['path']}")
    if lock["id"] == "team-ram":
        for relative in (".mcp.json", ".claude-plugin/.mcp.json"):
            config = read_json(output / relative)
            servers = config.get("mcpServers", {})
            if not servers or any("env" in value for value in servers.values() if isinstance(value, dict)):
                raise ExportError(f"team-ram: {relative} contains embedded MCP environment credentials")
            for value in servers.values():
                if not isinstance(value, dict) or value.get("url") != "http://localhost:5888/mcp":
                    raise ExportError(f"team-ram: {relative} contains an unapproved MCP endpoint or shape")
        print("  Team RAM MCP inspection: localhost-only endpoints; no embedded credentials")
    if (output / ".mcp.json").exists() and lock["id"] == "mortagate-cowork":
        raise ExportError("mortagate: dirty repository-root .mcp.json leaked into export")


def validate_versions(output: Path, lock: dict[str, Any], marketplace: dict[str, Any]) -> None:
    entries = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == lock.get("marketplaceAlias")]
    if lock["marketplace"]:
        if len(entries) != 1:
            raise ExportError(f"{lock['id']}: compatibility marketplace alias must resolve exactly once")
        entry = entries[0]
        if entry.get("source") != f"./{lock['destination']}":
            raise ExportError(f"{lock['id']}: marketplace alias source does not resolve to generated destination")
        if entry.get("version") != lock["runtimeVersion"]:
            raise ExportError(f"{lock['id']}: marketplace/runtime version mismatch")
        claude = read_json(output / ".claude-plugin/plugin.json")
        codex = read_json(output / ".codex-plugin/plugin.json")
        package = read_json(output / "package.json")
        if claude.get("name") != lock["sourceManifestName"] or codex.get("name") != lock["sourceManifestName"]:
            raise ExportError(f"{lock['id']}: source manifest identity mismatch; generated manifests must not be hand-edited to alias")
        if claude.get("version") != lock["runtimeVersion"] or codex.get("version") != lock["runtimeVersion"]:
            raise ExportError(f"{lock['id']}: Claude/Codex/runtime version parity failed")
        if package.get("name") != lock["sourcePackageName"] or package.get("version") != lock["packageVersion"]:
            raise ExportError(f"{lock['id']}: package identity/version does not match source lock")
        for field in ("skills", "agents", "commands", "hooks", "mcp"):
            value = claude.get(field)
            if isinstance(value, str) and not (output / value).exists():
                raise ExportError(f"{lock['id']}: Claude manifest {field} path does not resolve: {value}")
            if isinstance(value, list):
                for relative in value:
                    if not (output / relative).exists():
                        raise ExportError(f"{lock['id']}: Claude manifest {field} path does not resolve: {relative}")
        print(f"  compatibility alias: {lock['marketplaceAlias']} -> {lock['sourceManifestName']} v{lock['runtimeVersion']}")
    elif entries:
        raise ExportError(f"{lock['id']}: non-Claude runtime package must not appear in Claude marketplace")


def normalized_repo(value: str) -> str:
    return value.removesuffix(".git").rstrip("/")


def verify_source_receipt(output: Path, lock: dict[str, Any]) -> None:
    if lock["id"] == "team-ram":
        receipt = read_json(output / "EXPORT_PROVENANCE.json")
        source_contract = read_json(output / "SOURCE.json")
        if (
            receipt.get("generated") is not True
            or normalized_repo(receipt.get("sourceRepository", "")) != normalized_repo(lock["repository"])
            or receipt.get("sourceCommit") != lock["commit"]
            or receipt.get("manifest") != lock["manifest"]
            or source_contract.get("canonical") is not True
            or source_contract.get("authority", {}).get("manifest") != lock["manifest"]
            or normalized_repo(source_contract.get("repository", "")) != normalized_repo(lock["repository"])
        ):
            raise ExportError("team-ram source export provenance/source contract mismatch")
    elif lock["id"] == "team-durham":
        receipt = read_json(output / "EXPORT.json")
        source_contract = read_json(output / "SOURCE.json")
        if (
            receipt.get("sourceRevision") != lock["commit"]
            or receipt.get("sourceDirty") is not False
            or normalized_repo(receipt.get("sourceRepository", "")) != normalized_repo(lock["repository"])
            or source_contract.get("revision") != lock["commit"]
            or source_contract.get("exportManifest") != lock["manifest"]
            or source_contract.get("exportScript") != lock["exporter"]
            or normalized_repo(source_contract.get("canonicalRepository", "")) != normalized_repo(lock["repository"])
        ):
            raise ExportError("team-durham source export provenance/source contract mismatch")
        receipt_files = receipt.get("files", [])
        actual_files = [
            {"path": row["path"], "sha256": row["sha256"], "size": row["size"]}
            for row in tree_inventory(output) if row["kind"] == "file" and row["path"] != "EXPORT.json"
        ]
        if {row["path"]: row for row in receipt_files} != {row["path"]: row for row in actual_files}:
            raise ExportError("team-durham EXPORT.json per-file inventory mismatch")
    else:
        receipt = read_json(output / "EXPORT_PROVENANCE.json")
        if receipt.get("generated") is not True or receipt.get("authoritative") is not False or len(receipt.get("files", [])) != 19:
            raise ExportError("mortagate generated provenance/19-file inventory mismatch")


def compare_or_sync(expected: Path, destination: Path, sync: bool, lock: dict[str, Any]) -> None:
    expected_inventory = tree_inventory(expected)
    actual_inventory = tree_inventory(destination) if destination.is_dir() else []
    if expected_inventory == actual_inventory:
        print(f"  no drift: {lock['destination']} ({len(expected_inventory)} exported entries)")
        return
    expected_map = {row["path"]: row for row in expected_inventory}
    actual_map = {row["path"]: row for row in actual_inventory}
    missing = sorted(expected_map.keys() - actual_map.keys())
    unexpected = sorted(actual_map.keys() - expected_map.keys())
    changed = sorted(path for path in expected_map.keys() & actual_map.keys() if expected_map[path] != actual_map[path])
    if not sync:
        summary = f"missing={len(missing)}, unexpected={len(unexpected)}, changed={len(changed)}"
        details = (missing[:3] + unexpected[:3] + changed[:3])
        raise ExportError(f"{lock['id']}: generated export drift ({summary}); sample: {', '.join(details)}")
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or destination.is_file():
            destination.unlink()
        else:
            shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(expected, destination, symlinks=True)
    if tree_inventory(destination) != expected_inventory:
        raise ExportError(f"{lock['id']}: post-sync verification failed")
    print(f"  synced: {lock['destination']} ({len(expected_inventory)} exported entries)")


def selected_locks(all_locks: list[dict[str, Any]], selectors: list[str]) -> list[dict[str, Any]]:
    if not selectors or "all" in selectors:
        return all_locks
    selected: list[dict[str, Any]] = []
    for selector in selectors:
        matches = [lock for lock in all_locks if selector == lock["id"] or selector in lock["aliases"]]
        if len(matches) != 1:
            raise ExportError(f"unknown or ambiguous package alias: {selector}")
        if matches[0] not in selected:
            selected.append(matches[0])
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if catalog differs from pinned source exports")
    mode.add_argument("--sync", action="store_true", help="replace selected destinations with pinned source exports")
    parser.add_argument("--package", action="append", default=[], help="source id or compatibility alias; repeatable (default: all)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        lock_data = read_json(LOCKS_PATH)
        if lock_data.get("schemaVersion") != 1 or lock_data.get("policy", {}).get("manualEdits") != "forbidden":
            raise ExportError("source-locks.json policy/schema is invalid")
        locks = lock_data.get("sources", [])
        if not isinstance(locks, list) or not locks:
            raise ExportError("source-locks.json has no sources")
        for lock in locks:
            validate_lock(lock)
        locks = selected_locks(locks, args.package)
        marketplace = read_json(MARKETPLACE_PATH)
        with tempfile.TemporaryDirectory(prefix="allura-source-exports-") as directory:
            temporary = Path(directory)
            for lock in locks:
                print(f"[{lock['id']}] {lock['repository']}@{lock['commit']}")
                source = clone_pinned(lock, temporary / "sources")
                if not (source / lock["manifest"]).is_file():
                    raise ExportError(f"{lock['id']}: canonical manifest/contract missing")
                output = temporary / "exports" / lock["id"]
                output.parent.mkdir(parents=True, exist_ok=True)
                generate(lock, source, output)
                verify_no_secrets(output, lock)
                verify_source_receipt(output, lock)
                validate_versions(output, lock, marketplace)
                compare_or_sync(output, ROOT / lock["destination"], args.sync, lock)
        print(f"source export {'sync' if args.sync else 'check'} passed for {len(locks)} package(s)")
        return 0
    except ExportError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
