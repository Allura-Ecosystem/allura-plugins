import importlib.util
import json
from pathlib import Path


def test_metadata_check_is_read_only_and_sync_preserves_existing_policy(tmp_path):
    spec = importlib.util.spec_from_file_location("metadata", Path(__file__).resolve().parents[1] / "scripts/sync_catalog_metadata.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def write(relative, data):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))

    write("source-locks.json", {"sources": [{"id": "native", "aliases": ["native-alias"], "marketplace": False}]})
    write(".claude-plugin/marketplace.json", {"name": "test", "plugins": [{"name": "portable", "source": "./portable", "version": "old"}, {"name": "native-alias", "source": "./native"}]})
    policy = {"installation": "AVAILABLE", "authentication": "ON_USE"}
    write(".agents/plugins/marketplace.json", {"name": "test", "plugins": [{"name": "portable", "source": {"source": "local", "path": "./portable"}, "policy": policy}, {"name": "native-alias"}]})
    write("portable/.claude-plugin/plugin.json", {"version": "0.3.0", "description": "Portable fixture"})
    write("portable/.codex-plugin/plugin.json", {"name": "portable"})
    before = {path: path.read_bytes() for path in tmp_path.rglob("*.json")}
    assert len(module.synchronize(tmp_path, check=True)) == 2
    assert before == {path: path.read_bytes() for path in before}
    assert len(module.synchronize(tmp_path)) == 2
    assert module.synchronize(tmp_path, check=True) == []
    codex = json.loads((tmp_path / ".agents/plugins/marketplace.json").read_text())
    assert [item["name"] for item in codex["plugins"]] == ["portable"]
    assert codex["plugins"][0]["policy"] == policy
