"""Allura Brain governed-memory provider for Hermes Agent.

The provider uses the public Cloudflare tunnel only, hydrates relevant business
context before planning, and writes concise outcome traces after substantive
primary-agent turns. Credentials come from Hermes secret scope and are never
stored in this plugin's config file.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.memory_provider import MemoryProvider

from .client import AlluraBrainClient, checked_result
from .config import (PUBLIC_BRAIN_URL, load_config as _load_config,
                     secret_headers as _secret_headers, validate_group_id as _validate_group_id)

logger = logging.getLogger(__name__)

PROVIDER_NAME = "allura-brain"
_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:token|password|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+"),
)


def _redact(text: str) -> str:
    safe = text
    for pattern in _SECRET_PATTERNS:
        safe = pattern.sub(r"\1[REDACTED]", safe)
    return safe


class AlluraBrainProvider(MemoryProvider):
    def __init__(self) -> None:
        self._client: Optional[AlluraBrainClient] = None
        self._config: Dict[str, Any] = {}
        self._hermes_home = ""
        self._session_id = ""
        self._platform = "cli"
        self._agent_context = "primary"
        self._sync_thread: Optional[threading.Thread] = None
        self._last_recall_count = 0

    @property
    def name(self) -> str:
        return PROVIDER_NAME

    def is_available(self) -> bool:
        """Local-only activation check; intentionally performs no network I/O."""
        try:
            config = _load_config()
            headers = _secret_headers(config["group_id"])
        except (ValueError, TypeError, OSError):
            return False
        return (
            config.get("brain_url") == PUBLIC_BRAIN_URL
            and bool(headers.get("Authorization"))
            and bool(headers.get("CF-Access-Client-Id"))
            and bool(headers.get("CF-Access-Client-Secret"))
        )

    def unavailable_reason(self) -> str:
        return (
            "Allura Brain requires the public tunnel, "
            "an explicit valid profile group_id, ALLURA_MCP_TOKEN (or the scoped legacy alias), "
            "ALLURA_CF_ACCESS_CLIENT_ID, and "
            "ALLURA_CF_ACCESS_CLIENT_SECRET."
        )

    def initialize(self, session_id: str, **kwargs: Any) -> None:
        self._session_id = session_id
        self._hermes_home = kwargs.get(
            "hermes_home", os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
        )
        self._platform = kwargs.get("platform", "cli")
        self._agent_context = kwargs.get("agent_context", "primary")
        self._config = _load_config(self._hermes_home)
        url = self._config.get("brain_url", PUBLIC_BRAIN_URL)
        if url != PUBLIC_BRAIN_URL:
            raise ValueError(
                f"Allura Brain provider refuses non-canonical endpoint: {url!r}"
            )
        self._client = AlluraBrainClient(
            url=url,
            headers=_secret_headers(self._config["group_id"]),
            timeout=float(self._config.get("timeout", 30.0)),
        )

    def system_prompt_block(self) -> str:
        group_id = self._config.get("group_id")
        return (
            "\n## Allura Brain governed memory\n"
            f"Scoped tenant: `{group_id}`. Identity is supplied by authenticated transport.\n"
            "Retrieve Allura context before planning when prior decisions or operations matter. "
            "After substantive work, persist a concise outcome—not a raw transcript. "
            "Never store credentials or secret values. Use the public Cloudflare MCP tunnel only.\n"
        )

    def _search(self, query: str, limit: int) -> Dict[str, Any]:
        if not self._client:
            return {"results": []}
        return self._client.call_tool(
            "memory_search",
            {
                "query": query,
                "group_id": _validate_group_id(self._config.get("group_id")),
                "limit": limit,
                "include_global": False,
                "status": "all",
            },
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        self._last_recall_count = 0
        if not query.strip() or not self._client:
            return ""
        try:
            result = checked_result(self._search(query, 5))
            rows = result.get("results", [])
            self._last_recall_count = len(rows)
            if not rows:
                return ""
            lines = ["## Recalled from Allura Brain"]
            for row in rows:
                content = _redact(str(row.get("content", "")))[:1000]
                score = float(row.get("score", 0) or 0)
                lines.append(f"- [score={score:.2f}] {content}")
            return "\n".join(lines)
        except Exception as exc:
            logger.warning("Allura ambient recall failed: %s", exc)
            return ""

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if self._agent_context != "primary" or not self._client:
            return
        mode = self._config.get("sync_mode", "outcomes_only")
        if mode == "off":
            return
        user = _redact((user_content or "").strip())[:400]
        assistant = _redact((assistant_content or "").strip())[:900]
        if len(user) + len(assistant) < 120:
            return

        def _persist() -> None:
            try:
                if mode == "full":
                    content = f"TURN — intent: {user}\noutcome: {assistant}"
                else:
                    outcome = assistant.split("\n\n", 1)[0][:500]
                    content = f"OUTCOME — intent: {user[:240]} → {outcome}"
                self._client and self._client.call_tool(
                    "memory_add",
                    {
                        "group_id": _validate_group_id(self._config.get("group_id")),
                        "content": content,
                        "metadata": {
                            "source": "conversation",
                            "conversation_id": session_id or self._session_id,
                        },
                    },
                )
            except Exception as exc:
                logger.warning("Allura ambient persist failed: %s", exc)

        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5)
        self._sync_thread = threading.Thread(target=_persist, daemon=True)
        self._sync_thread.start()

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "allura_recall",
                "description": "Search governed Allura memory before planning or deciding.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "integer", "default": 10},
                        "group_id": {"type": "string"},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "allura_remember",
                "description": "Persist a concise sanitized business outcome to Allura.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "group_id": {"type": "string"},
                        "metadata": {"type": "object"},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "allura_governance_check",
                "description": "Evaluate all six governance invariants before a risky action.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "group_id": {"type": "string"},
                        "context": {"type": "object"},
                    },
                    "required": ["action"],
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs: Any) -> str:
        if not self._client:
            return json.dumps({"error": "Allura Brain provider is not initialized"})
        try:
            group_id = _validate_group_id(self._config.get("group_id"))
            if "group_id" in args and _validate_group_id(args["group_id"]) != group_id:
                raise ValueError("Cross-tenant override refused")
            if tool_name == "allura_recall":
                result = self._client.call_tool(
                    "memory_search",
                    {
                        "query": args["query"],
                        "group_id": group_id,
                        "limit": args.get("limit", 10),
                        "include_global": False,
                        "status": "all",
                    },
                )
            elif tool_name == "allura_remember":
                supplied = args.get("metadata") or {}
                if not isinstance(supplied, dict):
                    raise ValueError("metadata must be an object")
                metadata = {"conversation_id": self._session_id}
                if isinstance(supplied.get("conversation_id"), str):
                    metadata["conversation_id"] = supplied["conversation_id"]
                metadata.update(
                    {
                        "source": "conversation",
                    }
                )
                result = self._client.call_tool(
                    "memory_add",
                    {
                        "group_id": group_id,
                        "content": _redact(args["content"]),
                        "metadata": metadata,
                    },
                )
            elif tool_name == "allura_governance_check":
                result = self._client.call_tool(
                    "governance_check_gate",
                    {
                        "group_id": group_id,
                        "action": args["action"],
                        "context": args.get("context", {}),
                    },
                )
            else:
                result = {"error": f"Unknown Allura tool: {tool_name}"}
            return json.dumps(checked_result(result))
        except Exception as exc:
            logger.warning("Allura tool %s failed: %s", tool_name, exc)
            return json.dumps({"error": "Allura Brain tool call failed"})

    def on_session_switch(
        self,
        new_session_id: str,
        *,
        parent_session_id: str = "",
        reset: bool = False,
        rewound: bool = False,
        **kwargs: Any,
    ) -> None:
        self._session_id = new_session_id
        self._last_recall_count = 0

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=10)

    def shutdown(self) -> None:
        self.on_session_end([])
        self._client = None

    def get_config_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": "brain_url",
                "description": "Canonical Allura Brain public MCP endpoint",
                "default": PUBLIC_BRAIN_URL,
                "required": True,
            },
            {
                "key": "group_id",
                "description": "Explicit authorized allura-* tenant (required; no default)",
                "required": True,
            },
            {
                "key": "sync_mode",
                "description": "Ambient persistence mode",
                "choices": ["off", "outcomes_only", "full"],
                "default": "outcomes_only",
            },
        ]

    def save_config(self, values: Dict[str, Any], hermes_home: str) -> None:
        config = _load_config(hermes_home, values=values)
        path = Path(hermes_home) / "allura-brain.json"
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        path.chmod(0o600)


def register(ctx: Any) -> None:
    ctx.register_memory_provider(AlluraBrainProvider())
