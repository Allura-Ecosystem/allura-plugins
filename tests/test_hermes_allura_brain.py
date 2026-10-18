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
    for child in ("client", "config", "cli"):
        sys.modules.pop(f"{name}.{child}", None)
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
    with pytest.raises(ValueError):
        plugin._validate_group_id(None)
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
        lambda hermes_home=None: {"brain_url": plugin.PUBLIC_BRAIN_URL, "group_id": "allura-system"},
    )
    monkeypatch.setattr(
        plugin,
        "_secret_headers",
        lambda group_id: {
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


def test_prefetch_and_deliberate_write_use_transport_identity(monkeypatch):
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
    assert "user_id" not in search_args
    assert search_args["status"] == "all"
    assert search_args["include_global"] is False

    result = json.loads(
        provider.handle_tool_call(
            "allura_remember",
            {"content": "rotation complete token=do-not-store"},
        )
    )
    assert result == {"ok": True}
    add_args = fake.calls[-1][1]
    assert "user_id" not in add_args
    assert set(add_args["metadata"]) == {"source", "conversation_id"}
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
    assert set(args["metadata"]) == {"source", "conversation_id"}
    assert "user_id" not in args


def load_cli(plugin):
    import importlib
    return importlib.import_module(f"{plugin.__name__}.cli")


@pytest.mark.parametrize("group", [None, "", "allura-", "allura-UPPER", "allura-a_b", "allura-a\n", "foreign-project", 7])
def test_invalid_scope_never_looks_up_credentials(group, monkeypatch, tmp_path):
    plugin = load_plugin()
    config = sys.modules[f"{plugin.__name__}.config"]
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    (tmp_path / "allura-brain.json").write_text(json.dumps({"group_id": group}))
    monkeypatch.setattr(config, "get_secret", lambda *_: pytest.fail("credentials consulted before scope validation"))
    assert plugin.AlluraBrainProvider().is_available() is False
    with pytest.raises(ValueError):
        plugin.AlluraBrainProvider().initialize("test", hermes_home=str(tmp_path))
    assert load_cli(plugin)._test() == 1
    with pytest.raises(ValueError):
        config.secret_headers(group)


@pytest.mark.parametrize("raw", [None, "[1]", "{", '{}'])
def test_bad_or_missing_profile_fails_consistently(raw, monkeypatch, tmp_path):
    plugin = load_plugin()
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    config = sys.modules[f"{plugin.__name__}.config"]
    monkeypatch.setattr(config, "get_secret", lambda *_: pytest.fail("secret lookup"))
    if raw is not None:
        (tmp_path / "allura-brain.json").write_text(raw)
    assert plugin.AlluraBrainProvider().is_available() is False
    with pytest.raises(ValueError):
        plugin.AlluraBrainProvider().initialize("test", hermes_home=str(tmp_path))
    cli = load_cli(plugin)
    assert cli._load_cli_config is plugin._load_config
    assert cli._test() == 1
    assert cli._status() == 1
    with pytest.raises(SystemExit) as exc:
        cli.allura_brain_command(types.SimpleNamespace(allura_brain_command="config"))
    assert exc.value.code == 1


@pytest.mark.parametrize("group,expected", [("allura-system", "desktop"), ("allura-faithmeats", "admin"), ("allura-other", None)])
def test_token_alias_is_tenant_bound_and_generic_has_priority(group, expected, monkeypatch):
    plugin = load_plugin()
    config = sys.modules[f"{plugin.__name__}.config"]
    secrets = {"ALLURA_MCP_TROY_DESKTOP_TOKEN": "desktop", "ALLURA_MCP_TROY_ADMIN_TOKEN": "admin"}
    accessed = []
    monkeypatch.setattr(config, "get_secret", lambda name, default="": accessed.append(name) or secrets.get(name, default))
    headers = config.secret_headers(group)
    assert headers.get("Authorization") == (f"Bearer {expected}" if expected else None)
    if group != "allura-faithmeats":
        assert "ALLURA_MCP_TROY_ADMIN_TOKEN" not in accessed
    secrets["ALLURA_MCP_TOKEN"] = "generic"
    accessed.clear()
    assert config.secret_headers(group)["Authorization"] == "Bearer generic"
    assert "ALLURA_MCP_TROY_ADMIN_TOKEN" not in accessed
    assert "ALLURA_MCP_TROY_DESKTOP_TOKEN" not in accessed


def test_no_desktop_to_admin_fallback(monkeypatch):
    plugin = load_plugin()
    config = sys.modules[f"{plugin.__name__}.config"]
    monkeypatch.setattr(config, "get_secret", lambda name, default="": "admin" if name == "ALLURA_MCP_TROY_ADMIN_TOKEN" else default)
    assert "Authorization" not in config.secret_headers("allura-system")


@pytest.mark.parametrize("tool,args", [("allura_recall", {"query": "test"}), ("allura_remember", {"content": "outcome"}), ("allura_governance_check", {"action": "test"})])
def test_per_call_scope_cannot_escape_profile(tool, args):
    plugin = load_plugin()
    provider = plugin.AlluraBrainProvider()
    provider._config = {"group_id": "allura-system"}
    provider._client = FakeClient()
    assert "error" in json.loads(provider.handle_tool_call(tool, dict(args, group_id="allura-other")))
    assert provider._client.calls == []
    assert "error" not in json.loads(provider.handle_tool_call(tool, dict(args, group_id="allura-system")))
    assert len(provider._client.calls) == 1


def test_deliberate_metadata_is_narrow_and_identity_unasserted():
    plugin = load_plugin()
    provider = plugin.AlluraBrainProvider()
    provider._config = {"group_id": "allura-system", "agent_id": "unverified-persona"}
    provider._client = FakeClient()
    provider.handle_tool_call("allura_remember", {"content": "checked", "metadata": {"source": "wrong", "agent_id": "wrong", "platform": "cli", "sync_mode": "full", "conversation_id": "receipt"}})
    args = provider._client.calls[0][1]
    assert "user_id" not in args
    assert args["metadata"] == {"source": "conversation", "conversation_id": "receipt"}
    assert "unverified-persona" not in provider.system_prompt_block()


@pytest.mark.parametrize("result,expected", [({"results": []}, 0), ({"error": "TENANT_MISMATCH"}, 1), ({"isError": True}, 1), ({"success": False}, 1), ({"status": "error"}, 1), ({"raw": "something"}, 1), ({}, 1)])
def test_cli_checks_application_result(result, expected, monkeypatch, capsys):
    plugin = load_plugin()
    cli = load_cli(plugin)
    fake = FakeClient()
    fake.call_tool = lambda *_: result
    monkeypatch.setattr(cli, "_client", lambda: ({"group_id": "allura-system"}, fake))
    assert cli._test() == expected
    output = capsys.readouterr().out
    assert ("PASS" in output) is (expected == 0)


def test_cli_transport_failure_is_nonzero_and_redacted(monkeypatch, capsys):
    cli = load_cli(load_plugin())
    def fail():
        raise RuntimeError("Bearer sensitive-value")
    monkeypatch.setattr(cli, "_client", fail)
    assert cli._test() == 1
    assert "sensitive-value" not in capsys.readouterr().out


def test_save_config_creates_explicit_profile_and_preserves_existing_scope(tmp_path):
    plugin = load_plugin()
    provider = plugin.AlluraBrainProvider()
    with pytest.raises(ValueError):
        provider.save_config({}, str(tmp_path))
    assert not (tmp_path / "allura-brain.json").exists()
    provider.save_config({"group_id": "allura-system"}, str(tmp_path))
    provider.save_config({"sync_mode": "off"}, str(tmp_path))
    assert plugin._load_config(str(tmp_path))["group_id"] == "allura-system"
    with pytest.raises(ValueError):
        provider.save_config({"group_id": "bad"}, str(tmp_path))
    assert plugin._load_config(str(tmp_path))["group_id"] == "allura-system"
