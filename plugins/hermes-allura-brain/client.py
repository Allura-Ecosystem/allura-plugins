"""Authenticated Streamable HTTP client for Allura Brain."""

from __future__ import annotations

import asyncio
import json
import re
import threading
from typing import Any, Callable, Dict

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


def _safe_error(text: str) -> str:
    safe = re.sub(r"(?i)(bearer\s+)[^\s,;]+", r"\1[REDACTED]", text)
    safe = re.sub(
        r"(?i)((?:token|password|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+",
        r"\1[REDACTED]",
        safe,
    )
    return safe[:1000]


class AlluraBrainClient:
    """Open a short-lived authenticated MCP session for each operation."""

    def __init__(
        self,
        url: str,
        headers: Dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.url = url
        self.headers = dict(headers or {})
        self.timeout = timeout

    @staticmethod
    def _run_sync(factory: Callable[[], Any], timeout: float) -> Any:
        """Run an async factory from sync code, including inside a live event loop."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(factory())

        box: Dict[str, Any] = {}

        def _thread() -> None:
            try:
                box["result"] = asyncio.run(factory())
            except BaseException as exc:  # preserve the original exception
                box["error"] = exc

        worker = threading.Thread(target=_thread, daemon=True)
        worker.start()
        worker.join(timeout=timeout + 5)
        if worker.is_alive():
            raise TimeoutError("Allura Brain MCP operation timed out")
        if "error" in box:
            raise box["error"]
        return box.get("result")

    async def _with_session(self, operation: Callable[[ClientSession], Any]) -> Any:
        async with streamablehttp_client(
            self.url,
            headers=self.headers,
            timeout=self.timeout,
            sse_read_timeout=self.timeout,
        ) as (read, write, _get_session_id):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await operation(session)

    def is_reachable(self) -> bool:
        """Perform a real authenticated MCP initialize/list-tools round trip."""

        async def _probe() -> bool:
            result = await self._with_session(lambda session: session.list_tools())
            return bool(getattr(result, "tools", []))

        try:
            return bool(self._run_sync(_probe, self.timeout))
        except Exception:
            return False

    def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        async def _call() -> Dict[str, Any]:
            result = await self._with_session(
                lambda session: session.call_tool(tool_name, args)
            )
            texts = [
                text
                for block in (getattr(result, "content", None) or [])
                if (text := getattr(block, "text", None))
            ]
            raw = "\n".join(texts)
            if getattr(result, "isError", False) or getattr(result, "is_error", False):
                raise RuntimeError(
                    f"Allura Brain tool '{tool_name}' failed: {_safe_error(raw)}"
                )
            structured = getattr(result, "structuredContent", None)
            if isinstance(structured, dict):
                return structured
            try:
                return json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                return {"raw": raw}

        return self._run_sync(_call, self.timeout)
