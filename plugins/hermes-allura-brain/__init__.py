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
from agent.secret_scope import get_secret

from .client import AlluraBrainClient

logger = logging.getLogger(__name__)

PROVIDER_NAME = "allura-brain"
PUBLIC_BRAIN_URL = "https://mcp.faithmeats.org/mcp"
DEFAULT_GROUP_ID = "allura-faithmeats"
DEFAULT_AGENT_ID = "troy-admin"
LEGACY_PREFIXES = ("allura-roninmemory", "allura-team-ram", "roninclaw-")

_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[^\s,;]+"),
    re.compile(r"(?i)((?:token|password|secret|api[_-]?key)\s*[:=]\s*)[^\s,;]+"),
)


def _redact(text: str) -> str:
    safe = text
    for pattern in _SECRET_PATTERNS:
        safe = pattern.sub(r"\1[REDACTED]", safe)
    return safe


def _validate_group_id(group_id: Optional[str]) -> str:
    resolved = group_id or DEFAULT_GROUP_ID
    if not isinstance(resolved, str) or not resolved.startswith("allura-"):
        raise ValueError(f"Allura group_id must match allura-*; got {resolved!r}")
    if resolved.startswith(LEGACY_PREFIXES):
        raise ValueError(f"Allura legacy tenant is blocked: {resolved!r}")
    return resolved


def _load_config(hermes_home: str | None = None) -> Dict[str, Any]:
    home = Path(
        hermes_home
        or os.environ.get("HERMES_HOME")
        or Path.home() / ".hermes"
    )
    config: Dict[str, Any] = {
        "brain_url": PUBLIC_BRAIN_URL,
        "group_id": DEFAULT_GROUP_ID,
        "agent_id": DEFAULT_AGENT_ID,
        "sync_mode": "outcomes_only",
        "timeout": 30.0,
    }
    path = home / "allura-brain.json"
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except Exception as exc:
            logger.warning("Invalid allura-brain.json ignored: %s", exc)
    return config


def _secret_headers() -> Dict[str, str]:
    bearer = get_secret("ALLURA_MCP_TROY_ADMIN_TOKEN", "").strip()
    client_id = get_secret("ALLURA_CF_ACCESS_CLIENT_ID", "").strip()
    client_secret = get_secret("ALLURA_CF_ACCESS_CLIENT_SECRET", "").strip()
    headers: Dict[str, str] = {}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    if client_id:
        headers["CF-Access-Client-Id"] = client_id
    if client_secret:
        headers["CF-Access-Client-Secret"] = client_secret
    return headers


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
        config = _load_config()
        headers = _secret_headers()
        return (
            config.get("brain_url") == PUBLIC_BRAIN_URL
            and bool(headers.get("Authorization"))
            and bool(headers.get("CF-Access-Client-Id"))
            and bool(headers.get("CF-Access-Client-Secret"))
        )

    def unavailable_reason(self) -> str:
        return (
            "Allura Brain requires the public tunnel plus secret-scope values "
            "ALLURA_MCP_TROY_ADMIN_TOKEN, ALLURA_CF_ACCESS_CLIENT_ID, and "
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
            headers=_secret_headers(),
            timeout=float(self._config.get("timeout", 30.0)),
        )

    def system_prompt_block(self) -> str:
        group_id = self._config.get("group_id", DEFAULT_GROUP_ID)
        return (
            "\n## Allura Brain governed memory\n"
            f"Default tenant: `{group_id}`; principal: `{self._config.get('agent_id', DEFAULT_AGENT_ID)}`.\n"
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
                "user_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
                "limit": limit,
                "include_global": False,
            },
        )

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        self._last_recall_count = 0
        if not query.strip() or not self._client:
            return ""
        try:
            result = self._search(query, 5)
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
                        "user_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
                        "content": content,
                        "metadata": {
                            "source": "conversation",
                            "agent_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
                            "conversation_id": session_id or self._session_id,
                            "platform": self._platform,
                            "sync_mode": mode,
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
            group_id = _validate_group_id(
                args.get("group_id") or self._config.get("group_id")
            )
            if tool_name == "allura_recall":
                result = self._client.call_tool(
                    "memory_search",
                    {
                        "query": args["query"],
                        "group_id": group_id,
                        "user_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
                        "limit": args.get("limit", 10),
                        "include_global": False,
                    },
                )
            elif tool_name == "allura_remember":
                metadata = dict(args.get("metadata") or {})
                metadata.update(
                    {
                        "source": "conversation",
                        "agent_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
                    }
                )
                result = self._client.call_tool(
                    "memory_add",
                    {
                        "group_id": group_id,
                        "user_id": self._config.get("agent_id", DEFAULT_AGENT_ID),
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
            return json.dumps(result)
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
                "description": "Default allura-* tenant",
                "default": DEFAULT_GROUP_ID,
                "required": True,
            },
            {
                "key": "agent_id",
                "description": "Allura principal for reads and writes",
                "default": DEFAULT_AGENT_ID,
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
        config = _load_config(hermes_home)
        config.update(values)
        config["brain_url"] = PUBLIC_BRAIN_URL
        config["group_id"] = _validate_group_id(config.get("group_id"))
        path = Path(hermes_home) / "allura-brain.json"
        path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
        path.chmod(0o600)


def register(ctx: Any) -> None:
    ctx.register_memory_provider(AlluraBrainProvider())
