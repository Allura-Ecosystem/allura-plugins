"""Thin MCP streamable-HTTP client for Allura Brain.

Allura Brain at http://127.0.0.1:5888/mcp speaks streamable-HTTP/SSE
(Content-Type text/event-stream, mcp-session-id header). We use the
MCP Python SDK's streamablehttp_client + ClientSession — the same
transport proven in the AionUi integration (memory id 1c2382d7).

This client is deliberately minimal: connect, list tools, call tool.
No caching, no retries beyond the SDK defaults — Allura Brain is a
local endpoint with ~ms latency.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

logger = logging.getLogger(__name__)


class AlluraBrainClient:
    """Synchronous-ish wrapper over the async MCP streamable-HTTP transport.

    Each call_tool opens a fresh session (connect → call → close). This is
    simpler than managing a long-lived session across daemon threads and
    matches Brain's stateless-per-call semantics for memory_add/search/get.
    """

    def __init__(self, url: str = "http://127.0.0.1:5888/mcp", timeout: float = 30.0) -> None:
        self.url = url
        self.timeout = timeout

    def is_reachable(self) -> bool:
        """Quick readiness check — no MCP handshake, just HTTP probe to /ready."""
        import urllib.request
        try:
            ready_url = self.url.rstrip("/mcp") + "/ready"
            req = urllib.request.Request(ready_url, method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status == 200
        except Exception as e:
            logger.debug("Allura Brain /ready probe failed: %s", e)
            return False

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool on Allura Brain. Returns parsed JSON result.

        Raises RuntimeError on connection failure or tool error.
        """
        import asyncio

        async def _run() -> Dict[str, Any]:
            async with streamablehttp_client(self.url, timeout=self.timeout) as (read, write, _get_session_id):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, args)
                    # result.content is a list of content blocks; extract text
                    texts = []
                    for block in (result.content or []):
                        text = getattr(block, "text", None)
                        if text:
                            texts.append(text)
                    raw = "\n".join(texts) if texts else ""
                    if result.isError:
                        raise RuntimeError(f"Allura Brain tool '{tool_name}' returned error: {raw}")
                    # Brain tools return JSON strings; parse for the caller
                    import json
                    try:
                        return json.loads(raw) if raw else {}
                    except json.JSONDecodeError:
                        return {"raw": raw}

        try:
            return asyncio.run(_run())
        except RuntimeError as e:
            if "asyncio.run() cannot be called from a running event loop" in str(e):
                # Nested event loop — create a new loop in a thread
                import threading
                result_box: Dict[str, Any] = {}
                error_box: Optional[Exception] = None
                def _thread():
                    try:
                        result_box.update(asyncio.run(_run()))
                    except Exception as e:
                        error_box = e
                t = threading.Thread(target=_thread, daemon=True)
                t.start()
                t.join(timeout=self.timeout + 5)
                if error_box:
                    raise error_box
                return result_box
            raise