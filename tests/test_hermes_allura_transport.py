"""Regressions for old and new MCP client response/transport contracts."""

import asyncio
from contextlib import asynccontextmanager
import importlib.util
from pathlib import Path
import sys
import types
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1] / "plugins" / "hermes-allura-brain"


def load_client(name="transport_regression"):
    spec = importlib.util.spec_from_file_location(name, ROOT / "client.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def install_transport(monkeypatch, modern):
    calls = {}
    transport = types.ModuleType("mcp.client.streamable_http")
    mcp = types.ModuleType("mcp")

    @asynccontextmanager
    async def http_client(headers=None, timeout=None):
        calls.update(headers=headers, timeout=timeout)
        yield "http-client"
        calls["closed"] = True

    @asynccontextmanager
    async def connect(url, **kwargs):
        calls.update(url=url, kwargs=kwargs)
        yield ("read", "write") if modern else ("read", "write", None)

    class Session:
        def __init__(self, read, write):
            assert (read, write) == ("read", "write")

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def initialize(self):
            calls["initialized"] = True

        async def list_tools(self):
            return types.SimpleNamespace(tools=["memory_search"])

    mcp.ClientSession = Session
    if modern:
        transport.streamable_http_client = connect
        transport.create_mcp_http_client = http_client
    else:
        transport.streamablehttp_client = connect
    monkeypatch.setitem(sys.modules, "mcp", mcp)
    monkeypatch.setitem(sys.modules, "mcp.client.streamable_http", transport)
    return calls


@pytest.mark.parametrize("modern", [False, True])
def test_transport_api_generations(monkeypatch, modern):
    calls = install_transport(monkeypatch, modern)
    module = load_client()
    client = module.AlluraBrainClient(
        "https://example.invalid/mcp", {"Authorization": "Bearer test"}, 7
    )

    assert client.is_reachable()
    assert calls["initialized"]
    assert calls["url"] == client.url
    if modern:
        assert calls["headers"] == client.headers
        assert calls["timeout"] == 7
        assert calls["kwargs"] == {"http_client": "http-client"}
        assert calls["closed"]
    else:
        assert calls["kwargs"] == {
            "headers": client.headers,
            "timeout": 7,
            "sse_read_timeout": 7,
        }


@pytest.mark.parametrize(
    "attribute",
    ["structured_content", "structuredContent"],
)
def test_structured_response_generations(monkeypatch, attribute):
    install_transport(monkeypatch, modern=True)
    module = load_client(f"response_regression_{attribute}")
    client = module.AlluraBrainClient("https://example.invalid/mcp")
    result = types.SimpleNamespace(content=[], is_error=False)
    setattr(result, attribute, {"results": [{"id": attribute}]})

    async def response(operation):
        return result

    with patch.object(client, "_with_session", response):
        assert client.call_tool("memory_search", {}) == {
            "results": [{"id": attribute}]
        }


def _stuck(cancelled):
    async def stuck():
        try:
            await asyncio.sleep(0.08)
        finally:
            cancelled.append(True)

    return stuck


def test_sync_deadline_cancels_pending_request(monkeypatch):
    install_transport(monkeypatch, modern=True)
    module = load_client("deadline_regression")
    cancelled = []

    with pytest.raises(TimeoutError):
        module.AlluraBrainClient._run_sync(_stuck(cancelled), 0.01)
    assert cancelled == [True]


def test_sync_deadline_inside_event_loop_cancels_pending_request(monkeypatch):
    install_transport(monkeypatch, modern=True)
    module = load_client("event_loop_deadline_regression")
    cancelled = []

    async def invoke():
        with pytest.raises(TimeoutError):
            module.AlluraBrainClient._run_sync(_stuck(cancelled), 0.01)

    asyncio.run(invoke())
    assert cancelled == [True]
