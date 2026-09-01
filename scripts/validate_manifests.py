#!/usr/bin/env python3
"""Validate Allura plugin manifests, path references, and hardcoded absolute paths.

This script enforces the Story P-1.1 acceptance criteria for Marketplace CI Hardening:
  1. Target plugin manifests parse as JSON without errors.
  2. Every referenced file path in manifests resolves to a real file.
  3. No hardcoded absolute paths in any manifest or plugin source under each plugin.
  4. CI runs this validation on every push and blocks on failure.
  5. Marketplace sources resolve correctly (structural check only here).

Run: python3 scripts/validate_manifests.py
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ["allura-cowork", "team-durham", "team-ram-coding"]
MANIFEST_VARIANTS = [".claude-plugin/plugin.json", ".codex-plugin/plugin.json"]
MARKETPLACE = ".claude-plugin/marketplace.json"
HERMES_PLUGIN_MANIFEST = "plugins/hermes-allura-brain/plugin.yaml"
SOURCE_LOCKS = "source-locks.json"

# Catalog contract is deliberately declarative: portable marketplace packages and
# native providers have different public surfaces and must not be conflated.
PACKAGE_CONTRACTS = {
    "allura-cowork": {"kind": "portable", "readme": "README.md"},
    "team-durham": {"kind": "generated-portable", "readme": "README.md"},
    "team-ram-coding": {"kind": "generated-portable", "readme": "README.md"},
    "packages/mortagate-cowork": {"kind": "generated-runtime-neutral", "readme": "README.md"},
    "plugins/hermes-allura-brain": {"kind": "provider", "readme": "README.md"},
    "allura": {"kind": "internal-support", "readme": "README.md"},
}

# Paths that look like intentionally generic placeholders are allowed in documentation/examples.
# Anything under /home/<real-user>/, /Users/<real-user>/, /mnt/, or a Windows drive is forbidden.
HARDCODED_RE = re.compile(
    r"(?:/home/(?!user/)[^\s\"'\])}]+|/Users/[^\s\"'\])}]+|/mnt/[^\s\"'\])}]+|C:\\\\[^\s\"'\])}]+)"
)


def hard_fail(label: str, detail: str, errors: list) -> None:
    errors.append(f"{label}: {detail}")


def parse_json(path: Path, errors: list):
    """Parse a JSON file and return its data; record failure and return None otherwise."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        hard_fail("PARSE", f"{path} not found", errors)
    except json.JSONDecodeError as e:
        hard_fail("PARSE", f"{path} invalid JSON at line {e.lineno}, col {e.colno}: {e.msg}", errors)
    except Exception as e:
        hard_fail("PARSE", f"{path} unreadable: {e}", errors)
    return None


def check_marketplace(errors: list, warnings: list) -> None:
    mp_path = REPO_ROOT / MARKETPLACE
    if not mp_path.exists():
        hard_fail("MARKETPLACE", "marketplace.json missing", errors)
        return

    mp = parse_json(mp_path, errors)
    if mp is None:
        return

    plugins = mp.get("plugins")
    if not isinstance(plugins, list):
        hard_fail("MARKETPLACE", "top-level 'plugins' is not a list", errors)
        return

    names = set()
    for entry in plugins:
        name = entry.get("name")
        src = entry.get("source", "")
        version = entry.get("version", "")
        category = entry.get("category", "")

        if not name:
            hard_fail("MARKETPLACE", f"entry missing name (source={src})", errors)
            continue
        if name in names:
            hard_fail("MARKETPLACE", f"duplicate plugin name '{name}'", errors)
        names.add(name)

        # Structural expectations for Claude marketplace
        if not src:
            hard_fail("MARKETPLACE", f"{name} missing source", errors)
        elif src.startswith("/") or src.startswith(".."):
            hard_fail("MARKETPLACE", f"{name} source '{src}' escapes repo", errors)
        else:
            abs_src = REPO_ROOT / src
            if not abs_src.is_dir():
                hard_fail("MARKETPLACE", f"{name} source '{src}' does not resolve to directory", errors)
            else:
                print(f"  MARKETPLACE OK: {name} -> {src}")

        if not version:
            hard_fail("MARKETPLACE", f"{name} missing version", errors)
        if not category:
            warnings.append(f"MARKETPLACE: {name} missing category")


def check_manifests(errors: list, warnings: list) -> None:
    """Validate each target plugin's Claude and Codex manifests."""
    for plugin in PLUGINS:
        plugin_dir = REPO_ROOT / plugin
        for variant in MANIFEST_VARIANTS:
            manifest_path = plugin_dir / variant
            runtime = variant.split("/")[0].lstrip(".")
            data = parse_json(manifest_path, errors)
            if data is None:
                continue

            print(f"  MANIFEST PARSE OK: {plugin} ({runtime})")

            # Required fields sanity check
            for field in ("name", "version", "description"):
                if not data.get(field):
                    hard_fail("MANIFEST", f"{manifest_path} missing '{field}'", errors)

            # Paths declared in the manifest must resolve relative to the plugin root.
            refs = []
            for field in ("skills", "agents", "commands", "hooks"):
                value = data.get(field)
                if value is None:
                    continue
                if isinstance(value, str):
                    refs.append((field, value))
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, str):
                            refs.append((field, v))
                        else:
                            hard_fail("MANIFEST", f"{manifest_path} {field} contains non-string {v!r}", errors)
                else:
                    hard_fail("MANIFEST", f"{manifest_path} {field} has unexpected type {type(value).__name__}", errors)

            for field, ref in refs:
                target = plugin_dir / ref
                if not target.exists():
                    hard_fail("PATH", f"{manifest_path} declares {field}='{ref}' but file/directory missing", errors)
                else:
                    print(f"    PATH OK: {plugin}/{ref}")

            # Hook command strings inside hooks.json may contain shell expressions that reference
            # plugin-relative env vars; we treat them as runtime instructions, not filesystem refs.
            hooks_path = data.get("hooks")
            if hooks_path:
                resolved = plugin_dir / hooks_path
                if resolved.is_file():
                    hook_data = parse_json(resolved, errors)
                    if hook_data:
                        for event, entries in hook_data.get("hooks", {}).items():
                            for entry in entries:
                                if not isinstance(entry, dict):
                                    hard_fail("HOOK", f"{resolved} event {event} has non-object entry", errors)
                                    continue
                                for hook in entry.get("hooks", []):
                                    cmd = hook.get("command", "")
                                if isinstance(cmd, str) and cmd.startswith(("/", "C:")):
                                    hard_fail("HOOK", f"{resolved} event {event} uses absolute command path: {cmd}", errors)


def check_hermes_manifest(errors: list) -> None:
    """Validate the Hermes-native connector manifest without pretending it is a Claude package."""
    manifest_path = REPO_ROOT / HERMES_PLUGIN_MANIFEST
    if not manifest_path.exists():
        hard_fail("HERMES", f"native manifest missing at {HERMES_PLUGIN_MANIFEST}", errors)
        return

    fields: dict[str, str] = {}
    try:
        for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("-") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"').strip("'")
    except OSError as exc:
        hard_fail("HERMES", f"cannot read {manifest_path}: {exc}", errors)
        return

    for field in ("name", "version", "description"):
        if not fields.get(field):
            hard_fail("HERMES", f"{manifest_path} missing '{field}'", errors)

    if fields.get("name") != "allura-brain":
        hard_fail("HERMES", f"{manifest_path} name must be 'allura-brain'", errors)

    if not errors:
        print(f"  HERMES MANIFEST OK: {fields['name']} v{fields['version']}")


def _readme_has_contract(path: Path, required_markers: tuple[str, ...], errors: list) -> bool:
    if not path.is_file():
        hard_fail("CONTRACT", f"missing README at {path.relative_to(REPO_ROOT)}", errors)
        return False
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in required_markers if marker not in text]
    if missing:
        hard_fail(
            "CONTRACT",
            f"{path.relative_to(REPO_ROOT)} missing contract markers: {', '.join(missing)}",
            errors,
        )
        return False
    return True


def _hermes_manifest_version(errors: list) -> str:
    manifest = REPO_ROOT / HERMES_PLUGIN_MANIFEST
    if not manifest.is_file():
        return ""
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        if raw_line.strip().startswith("version:"):
            return raw_line.split(":", 1)[1].strip().strip('"').strip("'")
    hard_fail("CONTRACT", f"{HERMES_PLUGIN_MANIFEST} missing version", errors)
    return ""


def check_package_contracts(errors: list, warnings: list) -> None:
    """Verify each governed unit has the contract appropriate to its runtime."""
    marketplace = parse_json(REPO_ROOT / MARKETPLACE, errors) or {}
    lock_data = parse_json(REPO_ROOT / SOURCE_LOCKS, errors) or {}
    source_locks = {
        entry.get("destination"): entry
        for entry in lock_data.get("sources", [])
        if isinstance(entry, dict) and entry.get("destination")
    }
    marketplace_versions = {
        entry.get("name"): entry.get("version")
        for entry in marketplace.get("plugins", [])
        if isinstance(entry, dict)
    }

    portable_markers = (
        "## Package Contract",
        "### Runtime manifests",
        "### Validation",
        "### Dependencies and degraded behavior",
    )
    provider_markers = (
        "## Package Contract",
        "### Native provider manifest",
        "### Validation",
        "### Dependencies and degraded behavior",
    )

    for package, contract in PACKAGE_CONTRACTS.items():
        package_dir = REPO_ROOT / package
        kind = contract["kind"]
        readme = package_dir / contract["readme"]
        if not package_dir.is_dir():
            hard_fail("CONTRACT", f"package directory missing: {package}", errors)
            continue

        if kind == "portable":
            if not _readme_has_contract(readme, portable_markers, errors):
                continue
            package_json = parse_json(package_dir / "package.json", errors) or {}
            versions = [
                marketplace_versions.get(package),
                package_json.get("version"),
            ]
            for manifest in MANIFEST_VARIANTS:
                data = parse_json(package_dir / manifest, errors) or {}
                versions.append(data.get("version"))
            if not all(isinstance(version, str) and version for version in versions):
                hard_fail("CONTRACT", f"{package} has missing version metadata", errors)
                continue
            if len(set(versions)) != 1:
                hard_fail("CONTRACT", f"{package} version drift: {versions}", errors)
                continue
            print(f"  CONTRACT OK: {package} (portable) v{versions[0]}")
        elif kind == "generated-portable":
            if not readme.is_file():
                hard_fail("CONTRACT", f"generated package README missing: {readme.relative_to(REPO_ROOT)}", errors)
                continue
            receipt_name = "EXPORT_PROVENANCE.json" if package == "team-ram-coding" else "EXPORT.json"
            receipt = parse_json(package_dir / receipt_name, errors) or {}
            revision = receipt.get("sourceCommit") or receipt.get("sourceRevision")
            repository = receipt.get("sourceRepository", "")
            lock = source_locks.get(package, {})
            if not revision or not re.fullmatch(r"[0-9a-f]{40}", revision):
                hard_fail("CONTRACT", f"{package} generated provenance lacks a full source SHA", errors)
                continue
            if revision != lock.get("commit") or repository.removesuffix(".git") != str(lock.get("repository", "")).removesuffix(".git"):
                hard_fail("CONTRACT", f"{package} provenance does not match source-locks.json", errors)
                continue
            source_contract = parse_json(package_dir / "SOURCE.json", errors) or {}
            source_repo = source_contract.get("repository") or source_contract.get("canonicalRepository")
            source_manifest = source_contract.get("authority", {}).get("manifest") or source_contract.get("exportManifest")
            if str(source_repo).removesuffix(".git") != str(lock.get("repository", "")).removesuffix(".git") or source_manifest != lock.get("manifest"):
                hard_fail("CONTRACT", f"{package} SOURCE.json does not match its locked authority/manifest", errors)
                continue
            marketplace_alias = lock.get("marketplaceAlias")
            claude = parse_json(package_dir / ".claude-plugin/plugin.json", errors) or {}
            codex = parse_json(package_dir / ".codex-plugin/plugin.json", errors) or {}
            npm = parse_json(package_dir / "package.json", errors) or {}
            if marketplace_versions.get(marketplace_alias) != lock.get("runtimeVersion"):
                hard_fail("CONTRACT", f"{package} marketplace alias/runtime version mismatch", errors)
                continue
            if claude.get("name") != lock.get("sourceManifestName") or codex.get("name") != lock.get("sourceManifestName"):
                hard_fail("CONTRACT", f"{package} generated source manifest identity was changed", errors)
                continue
            if {claude.get("version"), codex.get("version")} != {lock.get("runtimeVersion")}:
                hard_fail("CONTRACT", f"{package} Claude/Codex runtime version mismatch", errors)
                continue
            if npm.get("name") != lock.get("sourcePackageName") or npm.get("version") != lock.get("packageVersion"):
                hard_fail("CONTRACT", f"{package} source package identity/version mismatch", errors)
                continue
            print(f"  CONTRACT OK: {package} (generated portable) @ {revision}")
        elif kind == "generated-runtime-neutral":
            if not readme.is_file():
                hard_fail("CONTRACT", f"generated package README missing: {readme.relative_to(REPO_ROOT)}", errors)
                continue
            receipt = parse_json(package_dir / "EXPORT_PROVENANCE.json", errors) or {}
            lock = source_locks.get(package, {})
            if receipt.get("generated") is not True or receipt.get("authoritative") is not False:
                hard_fail("CONTRACT", f"{package} provenance must mark generated/non-authoritative", errors)
                continue
            if receipt.get("sourceCommit") != lock.get("commit") or receipt.get("sourceRepository", "").removesuffix(".git") != str(lock.get("repository", "")).removesuffix(".git"):
                hard_fail("CONTRACT", f"{package} provenance does not match source-locks.json", errors)
                continue
            if receipt.get("contractPath") != lock.get("manifest") or len(receipt.get("files", [])) != 19:
                hard_fail("CONTRACT", f"{package} contract path or 19-file allowlist receipt is invalid", errors)
                continue
            if package in marketplace_versions:
                hard_fail("CONTRACT", f"{package} must not be listed in the Claude marketplace", errors)
                continue
            print(f"  CONTRACT OK: {package} (generated {receipt.get('runtime', 'runtime-neutral')})")
        elif kind == "provider":
            if not _readme_has_contract(readme, provider_markers, errors):
                continue
            version = _hermes_manifest_version(errors)
            if version:
                print(f"  CONTRACT OK: {package} (provider) v{version}")
        elif kind == "internal-support":
            if not _readme_has_contract(
                readme,
                ("## Internal support status", "not marketplace-releasable"),
                errors,
            ):
                continue
            print(f"  CONTRACT OK: {package} (internal-support)")
        else:
            hard_fail("CONTRACT", f"{package} has unknown contract kind {kind!r}", errors)


def check_hardcoded_paths(errors: list, warnings: list) -> None:
    """Scan manifests and plugin sources for hardcoded absolute paths."""
    text_extensions = {
        ".json", ".md", ".ts", ".js", ".py", ".sh", ".yaml", ".yml",
        ".css", ".scss", ".html", ".txt", ".toml", ".jsonc",
    }

    for plugin in PLUGINS:
        plugin_dir = REPO_ROOT / plugin
        for root, dirs, files in os.walk(plugin_dir):
            # Skip dependency/build artifacts
            dirs[:] = [d for d in dirs if d not in {"node_modules", "__pycache__", ".git", "dist", "build"}]
            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext not in text_extensions and not fname.endswith(".jsonc"):
                    continue
                fpath = Path(root) / fname
                try:
                    text = fpath.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                for m in HARDCODED_RE.finditer(text):
                    # Skip the intentionally generic /home/user/projects placeholder used in docs.
                    snippet = text[max(0, m.start() - 20):m.end() + 20]
                    if "/home/user/projects" in m.group(0):
                        continue
                    hard_fail("HARDCODED", f"{fpath}: absolute path {m.group(0)!r} near: ...{snippet!r}...", errors)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    print("== Allura Plugin Manifest Hardening Validator ==\n")

    print("[1] Marketplace source resolution")
    check_marketplace(errors, warnings)

    print("\n[2] Manifest parsing + referenced path resolution")
    check_manifests(errors, warnings)

    print("\n[3] Hardcoded absolute path sweep")
    check_hardcoded_paths(errors, warnings)

    print("\n[4] Hermes native manifest")
    check_hermes_manifest(errors)

    print("\n[5] Package contracts")
    check_package_contracts(errors, warnings)

    print("\n" + "=" * 50)
    if warnings:
        print("Warnings:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print("FAILURES:")
        for e in errors:
            print(f"  ❌ {e}")
        print(f"\n❌ Validation failed: {len(errors)} error(s).")
        return 1

    print("\n✅ All plugin manifests, references, and source files pass hardening checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
