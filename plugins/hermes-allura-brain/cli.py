"""CLI for the Allura Brain Hermes memory provider.

This module must remain importable without executing the provider __init__.py;
Hermes discovers memory-provider CLIs through a synthetic package shell.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from agent.secret_scope import get_secret

from .client import AlluraBrainClient

PUBLIC_BRAIN_URL = "https://mcp.faithmeats.org/mcp"
DEFAULT_GROUP_ID = "allura-faithmeats"
DEFAULT_AGENT_ID = "troy-admin"


def _load_cli_config() -> dict:
    home = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
    config = {
        "brain_url": PUBLIC_BRAIN_URL,
        "group_id": DEFAULT_GROUP_ID,
        "agent_id": DEFAULT_AGENT_ID,
        "sync_mode": "outcomes_only",
        "timeout": 30,
    }
    path = home / "allura-brain.json"
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            config.update(loaded)
    return config


def _cli_headers() -> dict[str, str]:
    bearer = get_secret("ALLURA_MCP_TROY_ADMIN_TOKEN", "").strip()
    client_id = get_secret("ALLURA_CF_ACCESS_CLIENT_ID", "").strip()
    client_secret = get_secret("ALLURA_CF_ACCESS_CLIENT_SECRET", "").strip()
    headers = {}
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"
    if client_id:
        headers["CF-Access-Client-Id"] = client_id
    if client_secret:
        headers["CF-Access-Client-Secret"] = client_secret
    return headers


def _client():
    config = _load_cli_config()
    return config, AlluraBrainClient(
        url=config.get("brain_url", PUBLIC_BRAIN_URL),
        headers=_cli_headers(),
        timeout=float(config.get("timeout", 30)),
    )


def _status() -> int:
    config, client = _client()
    headers = _cli_headers()
    configured = {
        "bearer": bool(headers.get("Authorization")),
        "cf_access_client_id": bool(headers.get("CF-Access-Client-Id")),
        "cf_access_client_secret": bool(headers.get("CF-Access-Client-Secret")),
    }
    print("Allura Brain Memory Provider")
    print(f"  URL:       {config.get('brain_url')}")
    print(f"  group_id:  {config.get('group_id', DEFAULT_GROUP_ID)}")
    print(f"  agent_id:  {config.get('agent_id', DEFAULT_AGENT_ID)}")
    print(f"  sync_mode: {config.get('sync_mode', 'outcomes_only')}")
    print(f"  secrets:   {json.dumps(configured, sort_keys=True)}")
    reachable = client.is_reachable()
    print(f"  MCP:       {'CONNECTED' if reachable else 'UNREACHABLE'}")
    return 0 if reachable else 1


def _test() -> int:
    config, client = _client()
    result = client.call_tool(
        "memory_search",
        {
            "query": "Epic 24 exit gate",
            "group_id": config.get("group_id", DEFAULT_GROUP_ID),
            "user_id": config.get("agent_id", DEFAULT_AGENT_ID),
            "limit": 1,
            "include_global": False,
        },
    )
    print(f"Authenticated search completed; results={len(result.get('results', []))}")
    print("PASS")
    return 0


def allura_brain_command(args) -> None:
    command = getattr(args, "allura_brain_command", None)
    if command == "status":
        raise SystemExit(_status())
    if command == "config":
        print(json.dumps(_load_cli_config(), indent=2, sort_keys=True))
        return
    if command == "test":
        raise SystemExit(_test())
    print("Usage: hermes allura-brain <status|config|test>")


def register_cli(subparser) -> None:
    subs = subparser.add_subparsers(dest="allura_brain_command")
    subs.add_parser("status", help="Show sanitized config and live MCP status")
    subs.add_parser("config", help="Show non-secret provider config")
    subs.add_parser("test", help="Run an authenticated read-only memory search")
    subparser.set_defaults(func=allura_brain_command)
