from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1] / "plugins" / "hermes-allura-brain"


def _install_agent_test_stubs() -> None:
    """Make provider unit tests independent of an installed Hermes checkout."""
    if importlib.util.find_spec("agent") is not None:
        return
    agent = types.ModuleType("agent")
    agent.__path__ = []
    memory_provider = types.ModuleType("agent.memory_provider")
    secret_scope = types.ModuleType("agent.secret_scope")

    class MemoryProvider:
        pass

    setattr(memory_provider, "MemoryProvider", MemoryProvider)
    setattr(secret_scope, "get_secret", lambda _name, default="": default)
    sys.modules.setdefault("agent", agent)
    sys.modules.setdefault("agent.memory_provider", memory_provider)
    sys.modules.setdefault("agent.secret_scope", secret_scope)

    if importlib.util.find_spec("mcp") is None:
        mcp = types.ModuleType("mcp")
        mcp.__path__ = []
        mcp_client = types.ModuleType("mcp.client")
        mcp_client.__path__ = []
        streamable_http = types.ModuleType("mcp.client.streamable_http")

        class ClientSession:
            pass

        setattr(mcp, "ClientSession", ClientSession)
        setattr(streamable_http, "streamablehttp_client", lambda *_args, **_kwargs: None)
        sys.modules.setdefault("mcp", mcp)
        sys.modules.setdefault("mcp.client", mcp_client)
        sys.modules.setdefault("mcp.client.streamable_http", streamable_http)


_install_agent_test_stubs()


def load_plugin():
    name = "allura_brain_test_plugin"
    sys.modules.pop(name, None)
    sys.modules.pop(f"{name}.client", None)
    spec = importlib.util.spec_from_file_location(
        name,
        ROOT / "__init__.py",
        submodule_search_locations=[str(ROOT)],
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FakeClient:
    def __init__(self):
        self.calls = []

    def call_tool(self, name, args):
        self.calls.append((name, args))
        if name == "memory_search":
            return {"results": [{"content": "verified context", "score": 0.9}]}
        return {"ok": True}


def test_cli_imports_through_hermes_synthetic_package():
    namespace = "_hermes_user_memory"
    package_name = f"{namespace}.allura-brain"
    for name, paths in ((namespace, []), (package_name, [str(ROOT)])):
        module = types.ModuleType(name)
        module.__path__ = paths
        sys.modules[name] = module
    module_name = f"{package_name}.cli"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "cli.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    assert callable(module.register_cli)
    assert callable(module.allura_brain_command)


def test_group_guard_blocks_legacy_and_non_allura():
    plugin = load_plugin()
    assert plugin._validate_group_id(None) == "allura-faithmeats"
    with pytest.raises(ValueError):
        plugin._validate_group_id("team-ram")
    with pytest.raises(ValueError):
        plugin._validate_group_id("allura-team-ram")


def test_redaction_removes_secret_values():
    plugin = load_plugin()
    text = "Authorization: Bearer abc123 token=secret123 password=hunter2"
    safe = plugin._redact(text)
    assert "abc123" not in safe
    assert "secret123" not in safe
    assert "hunter2" not in safe
    assert safe.count("[REDACTED]") == 3


def test_is_available_is_local_only(monkeypatch):
    plugin = load_plugin()
    monkeypatch.setattr(
        plugin,
        "_load_config",
        lambda hermes_home=None: {"brain_url": plugin.PUBLIC_BRAIN_URL},
    )
    monkeypatch.setattr(
        plugin,
        "_secret_headers",
        lambda: {
            "Authorization": "Bearer test",
            "CF-Access-Client-Id": "id",
            "CF-Access-Client-Secret": "secret",
        },
    )
    assert plugin.AlluraBrainProvider().is_available() is True


def test_initialize_refuses_local_or_lan_endpoint(monkeypatch, tmp_path):
    plugin = load_plugin()
    monkeypatch.setattr(
        plugin,
        "_load_config",
        lambda hermes_home=None: {
            "brain_url": "http://127.0.0.1:6477/mcp",
            "group_id": "allura-faithmeats",
            "agent_id": "troy-admin",
        },
    )
    provider = plugin.AlluraBrainProvider()
    with pytest.raises(ValueError, match="refuses non-canonical"):
        provider.initialize("s1", hermes_home=str(tmp_path))


def test_prefetch_and_deliberate_write_use_troy_identity(monkeypatch):
    plugin = load_plugin()
    provider = plugin.AlluraBrainProvider()
    provider._config = {
        "group_id": "allura-faithmeats",
        "agent_id": "troy-admin",
    }
    fake = FakeClient()
    provider._client = fake

    recall = provider.prefetch("Epic 24", session_id="s1")
    assert "verified context" in recall
    search_args = fake.calls[0][1]
    assert search_args["group_id"] == "allura-faithmeats"
    assert search_args["user_id"] == "troy-admin"

    result = json.loads(
        provider.handle_tool_call(
            "allura_remember",
            {"content": "rotation complete token=do-not-store"},
        )
    )
    assert result == {"ok": True}
    add_args = fake.calls[-1][1]
    assert add_args["user_id"] == "troy-admin"
    assert "do-not-store" not in add_args["content"]


def test_sync_turn_persists_substantive_outcome():
    plugin = load_plugin()
    provider = plugin.AlluraBrainProvider()
    provider._session_id = "session-1"
    provider._platform = "telegram"
    provider._agent_context = "primary"
    provider._config = {
        "group_id": "allura-faithmeats",
        "agent_id": "troy-admin",
        "sync_mode": "outcomes_only",
    }
    fake = FakeClient()
    provider._client = fake

    provider.sync_turn(
        "Verify the Epic 24 acceptance criteria against repository evidence.",
        "Verified the story documents and recorded the corrected exit-gate status in Allura Brain.",
    )
    provider.on_session_end([])
    name, args = fake.calls[-1]
    assert name == "memory_add"
    assert args["metadata"]["conversation_id"] == "session-1"
    assert args["metadata"]["platform"] == "telegram"
    assert args["user_id"] == "troy-admin"
