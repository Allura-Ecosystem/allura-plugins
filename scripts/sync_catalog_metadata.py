#!/usr/bin/env python3
"""Synchronize release metadata from source locks and portable plugin manifests.

Does not install plugins or alter a user's runtime configuration.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def synchronize(root: Path, check: bool = False) -> list[str]:
    locks = json.loads((root / "source-locks.json").read_text())["sources"]
    claude_path = root / ".claude-plugin/marketplace.json"
    codex_path = root / ".agents/plugins/marketplace.json"
    claude = json.loads(claude_path.read_text())
    codex = json.loads(codex_path.read_text())
    native_names = {alias for lock in locks if not lock["marketplace"] for alias in [lock["id"], *lock["aliases"]]}
    # Native Microsoft/Hermes packages must not masquerade as portable plugins.
    claude["plugins"] = [entry for entry in claude["plugins"] if entry["name"] not in native_names]
    codex["plugins"] = [entry for entry in codex["plugins"] if entry["name"] not in native_names]
    for lock in locks:
        if not lock["marketplace"]:
            continue
        name = lock["marketplaceAlias"]
        matches = [entry for entry in claude["plugins"] if entry["name"] == name]
        if not matches:
            claude["plugins"].append({"name": name, "source": "./" + lock["destination"], "category": "Security" if name == "bumblebee" else "Productivity"})
    for entry in claude["plugins"]:
        plugin = root / entry["source"]
        manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
        entry["version"] = manifest["version"]
        entry["description"] = manifest["description"]
        if not (plugin / ".codex-plugin/plugin.json").is_file():
            continue
        if not any(item["name"] == entry["name"] for item in codex["plugins"]):
            codex["plugins"].append({
                "name": entry["name"],
                "source": {"source": "local", "path": entry["source"]},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": entry.get("category", "Productivity"),
            })
    changed = []
    for path, data in ((claude_path, claude), (codex_path, codex)):
        if json.loads(path.read_text()) != data:
            changed.append(str(path.relative_to(root)))
            if not check:
                path.write_text(json.dumps(data, indent=2) + "\n")
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = synchronize(ROOT, args.check)
    print(("Metadata drift: " if args.check else "Updated: ") + ", ".join(changed) if changed else "Catalog metadata is current")
    raise SystemExit(1 if args.check and changed else 0)
