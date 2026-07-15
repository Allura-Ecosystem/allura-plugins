"""Allura Brain memory provider for Hermes Agent.

Implements the MemoryProvider ABC to bridge Hermes's turn lifecycle to
Allura Brain's governed memory (PostgreSQL episodic + Neo4j semantic,
HITL curator promotion).

Design — hybrid ambient + deliberate:
  - prefetch():           ambient memory_search before each LLM call
  - sync_turn():          ambient memory_add of a CONCISE outcome trace
                          (not raw transcript — respects Allura curation)
  - get_tool_schemas():   explicit allura_recall / allura_remember /
                          allura_governance_check for deliberate ops
  - system_prompt_block(): governance rules + default group_id
  - on_pre_compress():    extract insights from messages about to be discarded

Governance guard (mirrors ~/.claude/plugins/allura-brain guard hook):
  - group_id must match allura-*
  - blocks legacy prefixes: allura-roninmemory, allura-team-ram, roninclaw-*
  - default group_id: allura-system

See: agent/memory_provider.py for the ABC.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.memory_provider import MemoryProvider

from .client import AlluraBrainClient

logger = logging.getLogger(__name__)

DEFAULT_GROUP_ID = "allura-system"
LEGACY_PREFIXES = ("allura-roninmemory", "allura-team-ram", "roninclaw-")
DEFAULT_AGENT_ID = "hermes-agent"


def _validate_group_id(group_id: Optional[str]) -> str:
    """Enforce allura-* namespace, block legacy prefixes. Returns resolved group_id."""
    if not group_id or not isinstance(group_id, str):
        return DEFAULT_GROUP_ID
    if group_id.startswith(LEGACY_PREFIXES):
        raise ValueError(
            f"Allura Brain blocked legacy group_id '{group_id}'. "
            f"Use '{DEFAULT_GROUP_ID}' or another approved allura-* tenant."
        )
    if not group_id.startswith("allura-"):
        raise ValueError(
            f"Allura Brain group_id must match allura-*; got '{group_id}'."
        )
    return group_id


class AlluraBrainProvider(MemoryProvider):
    """Hermes memory provider backed by Allura Brain governed memory."""

    def __init__(self) -> None:
        self._client: Optional[AlluraBrainClient] = None
        self._session_id: str = ""
        self._hermes_home: str = ""
        self._platform: str = "cli"
        self._agent_context: str = "primary"
        self._agent_identity: str = ""
        self._user_id: str = ""
        self._config: Dict[str, Any] = {}
        self._sync_thread: Optional[threading.Thread] = None
        self._prefetch_cache: Dict[str, str] = {}
        self._pending_prefetch: Optional[str] = None
        self._llm_complete = None  # set by initialize() if ctx.llm available

    # -- Core lifecycle ------------------------------------------------------

    @property
    def name(self) -> str:
        return "allura-brain"

    def is_available(self) -> bool:
        """Check config + reachability. No MCP handshake — just /ready probe."""
        url = self._load_config().get("brain_url", "http://127.0.0.1:5888/mcp")
        client = AlluraBrainClient(url=url)
        return client.is_reachable()

    def initialize(self, session_id: str, **kwargs) -> None:
        self._session_id = session_id
        self._hermes_home = kwargs.get("hermes_home", os.path.expanduser("~/.hermes"))
        self._platform = kwargs.get("platform", "cli")
        self._agent_context = kwargs.get("agent_context", "primary")
        self._agent_identity = kwargs.get("agent_identity", "")
        self._user_id = kwargs.get("user_id", "")

        self._config = self._load_config()
        self._client = AlluraBrainClient(
            url=self._config.get("brain_url", "http://127.0.0.1:5888/mcp"),
            timeout=float(self._config.get("timeout", 30.0)),
        )

        # LLM access for outcomes-only summarization (optional)
        # ctx.llm is not passed to initialize; providers that want it
        # capture it via register() ctx. We store a reference there.
        logger.info(
            "AlluraBrainProvider initialized: session=%s platform=%s context=%s group=%s",
            session_id, self._platform, self._agent_context,
            self._config.get("group_id", DEFAULT_GROUP_ID),
        )

    def _load_config(self) -> Dict[str, Any]:
        """Load config from $HERMES_HOME/allura-brain.json, fall back to env then defaults."""
        config: Dict[str, Any] = {}
        # env defaults
        config["brain_url"] = os.environ.get("ALLURA_BRAIN_URL", "http://127.0.0.1:5888/mcp")
        config["group_id"] = os.environ.get("ALLURA_BRAIN_GROUP_ID", DEFAULT_GROUP_ID)
        config["agent_id"] = os.environ.get("ALLURA_BRAIN_AGENT_ID", DEFAULT_AGENT_ID)
        config["sync_mode"] = os.environ.get("ALLURA_BRAIN_SYNC_MODE", "outcomes_only")
        config["timeout"] = float(os.environ.get("ALLURA_BRAIN_TIMEOUT", "30"))
        # file overrides
        try:
            home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
            cfg_path = Path(home) / "allura-brain.json"
            if cfg_path.exists():
                file_cfg = json.loads(cfg_path.read_text())
                config.update(file_cfg)
        except Exception as e:
            logger.debug("Could not load allura-brain.json: %s", e)
        return config

    # -- System prompt -------------------------------------------------------

    def system_prompt_block(self) -> str:
        group_id = self._config.get("group_id", DEFAULT_GROUP_ID)
        return (
            "\n## Allura Brain Governed Memory\n"
            "You have access to Allura Brain — a governed memory system with "
            "PostgreSQL (episodic traces) and Neo4j (semantic, HITL-promoted) stores.\n\n"
            "Rules:\n"
            f"1. Default tenant: group_id='{group_id}'. Use this unless the active "
            "project explicitly declares another approved allura-* tenant.\n"
            "2. Retrieve before planning — use allura_recall or relevant context will "
            "be injected automatically before each turn.\n"
            "3. After substantive work, persist a concise outcome trace via "
            "allura_remember. Do NOT dump raw transcripts.\n"
            "4. Never use legacy tenants: allura-roninmemory, allura-team-ram, roninclaw-*.\n"
            "5. Never write secrets to memory.\n"
            "6. For risky actions, pre-flight with allura_governance_check.\n"
        )

    # -- Prefetch (ambient recall) ------------------------------------------

    def prefetch(self, query: str, *, session_id: str = "") -> str:
        """Return cached recall for the upcoming turn. Fast — uses background results."""
        if not query.strip():
            return ""
        cache_key = query.strip()[:200]
        if cache_key in self._prefetch_cache:
            return self._prefetch_cache.pop(cache_key)
        # No pending background prefetch — do a synchronous quick search
        return self._do_search(query, limit=3)

    def queue_prefetch(self, query: str, *, session_id: str = "") -> None:
        """Queue a background recall for the NEXT turn."""
        if not query.strip():
            return
        cache_key = query.strip()[:200]

        def _bg():
            try:
                result = self._do_search(query, limit=5)
                if result:
                    self._prefetch_cache[cache_key] = result
            except Exception as e:
                logger.debug("Background prefetch failed: %s", e)

        t = threading.Thread(target=_bg, daemon=True)
        t.start()

    def _do_search(self, query: str, limit: int = 5) -> str:
        if not self._client:
            return ""
        try:
            group_id = self._config.get("group_id", DEFAULT_GROUP_ID)
            result = self._client.call_tool("memory_search", {
                "query": query,
                "group_id": group_id,
                "limit": limit,
            })
            results = result.get("results", [])
            if not results:
                return ""
            lines = ["## Recalled from Allura Brain:"]
            for r in results[:limit]:
                score = r.get("score", 0)
                content = r.get("content", "")[:300]
                lines.append(f"- [score={score:.2f}] {content}")
            return "\n".join(lines) + "\n"
        except Exception as e:
            logger.debug("Allura recall failed: %s", e)
            return ""

    # -- Sync turn (ambient persist) ----------------------------------------

    def sync_turn(
        self,
        user_content: str,
        assistant_content: str,
        *,
        session_id: str = "",
        messages: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Persist a concise outcome trace after each turn. Non-blocking."""
        if self._agent_context != "primary":
            return  # don't write for cron/subagent/flush contexts

        mode = self._config.get("sync_mode", "outcomes_only")
        if mode == "off":
            return

        # Join any previous sync thread (bounded wait)
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=5.0)

        def _sync():
            try:
                content = self._build_sync_content(user_content, assistant_content, messages, mode)
                if not content:
                    return
                group_id = self._config.get("group_id", DEFAULT_GROUP_ID)
                agent_id = self._config.get("agent_id", DEFAULT_AGENT_ID)
                self._client and self._client.call_tool("memory_add", {
                    "group_id": group_id,
                    "user_id": agent_id,
                    "content": content,
                    "metadata": {
                        "source": "conversation",
                        "agent_id": agent_id,
                        "session_id": session_id or self._session_id,
                        "platform": self._platform,
                        "sync_mode": mode,
                    },
                })
            except Exception as e:
                logger.warning("Allura sync_turn failed: %s", e)

        self._sync_thread = threading.Thread(target=_sync, daemon=True)
        self._sync_thread.start()

    def _build_sync_content(
        self,
        user_content: str,
        assistant_content: str,
        messages: Optional[List[Dict[str, Any]]],
        mode: str,
    ) -> str:
        """Build the memory_add content per sync_mode."""
        user_trim = (user_content or "").strip()[:500]
        asst_trim = (assistant_content or "").strip()[:800]
        if not user_trim and not asst_trim:
            return ""
        if mode == "full":
            return f"TURN — user: {user_trim}\nassistant: {asst_trim}"
        # outcomes_only: concise summary line
        # Without host-owned LLM access from initialize, use a heuristic:
        # first sentence of assistant content + user intent prefix.
        first_sentence = asst_trim.split(".")[0][:200] if asst_trim else ""
        intent = user_trim[:120] if user_trim else "(no user input)"
        return f"OUTCOME — intent: {intent} → {first_sentence}"

    # -- Deliberate tools ----------------------------------------------------

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "allura_recall",
                "description": (
                    "Search Allura Brain governed memory for relevant context. "
                    "Use before planning or when you need prior decisions, outcomes, "
                    "or patterns. Federated search across PostgreSQL + Neo4j."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "group_id": {
                            "type": "string",
                            "description": "Tenant namespace (allura-*). Defaults to allura-system.",
                        },
                        "limit": {"type": "integer", "description": "Max results (default 10)", "default": 10},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "allura_remember",
                "description": (
                    "Persist a concise outcome trace to Allura Brain. Use after "
                    "substantive work — decisions, completed tasks, lessons learned. "
                    "Do NOT dump raw transcripts. Respect curation."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Memory content — concise outcome or decision"},
                        "group_id": {
                            "type": "string",
                            "description": "Tenant namespace (allura-*). Defaults to allura-system.",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional metadata (source, agent_id, conversation_id)",
                        },
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "allura_governance_check",
                "description": (
                    "Evaluate Allura governance invariants for a proposed action. "
                    "Returns pass/fail per invariant. Use before risky or destructive actions."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action being requested (e.g. 'memory_promote')"},
                        "group_id": {"type": "string", "description": "Tenant namespace"},
                        "context": {"type": "object", "description": "Additional context"},
                    },
                    "required": ["action", "group_id"],
                },
            },
        ]

    def handle_tool_call(self, tool_name: str, args: Dict[str, Any], **kwargs) -> str:
        if not self._client:
            return json.dumps({"error": "Allura Brain client not initialized"})
        try:
            if tool_name == "allura_recall":
                group_id = _validate_group_id(args.get("group_id") or self._config.get("group_id"))
                result = self._client.call_tool("memory_search", {
                    "query": args["query"],
                    "group_id": group_id,
                    "limit": args.get("limit", 10),
                })
                return json.dumps(result)
            elif tool_name == "allura_remember":
                group_id = _validate_group_id(args.get("group_id") or self._config.get("group_id"))
                metadata = args.get("metadata") or {}
                metadata.setdefault("source", "conversation")
                metadata.setdefault("agent_id", self._config.get("agent_id", DEFAULT_AGENT_ID))
                result = self._client.call_tool("memory_add", {
                    "group_id": group_id,
                    "user_id": metadata.get("agent_id", DEFAULT_AGENT_ID),
                    "content": args["content"],
                    "metadata": metadata,
                })
                return json.dumps(result)
            elif tool_name == "allura_governance_check":
                group_id = _validate_group_id(args.get("group_id"))
                result = self._client.call_tool("governance_check_gate", {
                    "group_id": group_id,
                    "action": args["action"],
                    "context": args.get("context", {}),
                })
                return json.dumps(result)
            else:
                return json.dumps({"error": f"Unknown tool: {tool_name}"})
        except ValueError as e:
            return json.dumps({"error": str(e)})
        except Exception as e:
            logger.warning("allura-brain tool '%s' failed: %s", tool_name, e)
            return json.dumps({"error": f"Allura Brain tool call failed: {e}"})

    # -- Optional hooks ------------------------------------------------------

    def on_pre_compress(self, messages: List[Dict[str, Any]]) -> str:
        """Extract insights from messages about to be discarded."""
        if not messages:
            return ""
        # Heuristic: surface any assistant messages containing decision keywords
        keywords = ("decision", "decided", "architecture", "blocker", "resolved", "lesson")
        insights: List[str] = []
        for msg in messages:
            if msg.get("role") != "assistant":
                continue
            content = (msg.get("content") or "")[:400]
            if any(kw in content.lower() for kw in keywords):
                insights.append(content[:200])
        if not insights:
            return ""
        return (
            "\n## Allura Brain pre-compress extraction:\n"
            "The following insights from discarded messages should be preserved:\n"
            + "\n---\n".join(insights[:3])
        )

    def on_session_end(self, messages: List[Dict[str, Any]]) -> None:
        """Final flush — ensure pending sync_turn thread completes."""
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=10.0)

    def shutdown(self) -> None:
        if self._sync_thread and self._sync_thread.is_alive():
            self._sync_thread.join(timeout=10.0)
        self._client = None
        logger.info("AlluraBrainProvider shut down.")

    # -- Config --------------------------------------------------------------

    def get_config_schema(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": "brain_url",
                "description": "Allura Brain MCP endpoint URL",
                "default": "http://127.0.0.1:5888/mcp",
                "required": True,
            },
            {
                "key": "group_id",
                "description": "Default tenant namespace (must match allura-*)",
                "default": DEFAULT_GROUP_ID,
                "required": True,
            },
            {
                "key": "agent_id",
                "description": "Hermes agent identity for memory writes",
                "default": DEFAULT_AGENT_ID,
                "required": False,
            },
            {
                "key": "sync_mode",
                "description": "What sync_turn persists after each turn",
                "choices": ["off", "outcomes_only", "full"],
                "default": "outcomes_only",
                "required": False,
            },
        ]

    def save_config(self, values: Dict[str, Any], hermes_home: str) -> None:
        cfg_path = Path(hermes_home) / "allura-brain.json"
        cfg_path.write_text(json.dumps(values, indent=2))
        logger.info("Allura Brain config saved to %s", cfg_path)


# -- Plugin entry point ------------------------------------------------------

def register(ctx) -> None:
    """Called by the memory plugin discovery system."""
    ctx.register_memory_provider(AlluraBrainProvider())