"""CLI subcommands for the Allura Brain memory provider.

Exposes: hermes allura-brain status | config | test
Only active when memory.provider == 'allura-brain'.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _load_config() -> dict:
    home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    cfg_path = Path(home) / "allura-brain.json"
    config = {
        "brain_url": os.environ.get("ALLURA_BRAIN_URL", "http://127.0.0.1:5888/mcp"),
        "group_id": os.environ.get("ALLURA_BRAIN_GROUP_ID", "allura-system"),
        "agent_id": os.environ.get("ALLURA_BRAIN_AGENT_ID", "hermes-agent"),
        "sync_mode": os.environ.get("ALLURA_BRAIN_SYNC_MODE", "outcomes_only"),
    }
    if cfg_path.exists():
        config.update(json.loads(cfg_path.read_text()))
    return config


def _cmd_status(args) -> None:
    cfg = _load_config()
    print("Allura Brain Memory Provider")
    print(f"  URL:       {cfg.get('brain_url')}")
    print(f"  group_id:  {cfg.get('group_id')}")
    print(f"  agent_id:  {cfg.get('agent_id')}")
    print(f"  sync_mode: {cfg.get('sync_mode')}")
    # Reachability probe
    try:
        import urllib.request
        ready_url = cfg.get("brain_url", "").rstrip("/mcp") + "/ready"
        with urllib.request.urlopen(ready_url, timeout=5) as resp:
            status = "REACHABLE" if resp.status == 200 else f"HTTP {resp.status}"
    except Exception as e:
        status = f"UNREACHABLE ({e})"
    print(f"  status:    {status}")


def _cmd_config(args) -> None:
    cfg = _load_config()
    print(json.dumps(cfg, indent=2))


def _cmd_test(args) -> None:
    """Round-trip: add a test memory, then search for it."""
    cfg = _load_config()
    from .client import AlluraBrainClient
    client = AlluraBrainClient(url=cfg.get("brain_url", "http://127.0.0.1:5888/mcp"))
    if not client.is_reachable():
        print("FAIL: Allura Brain not reachable")
        return
    import time
    token = f"hermes-plugin-test-{int(time.time())}"
    print(f"Adding test memory: {token}")
    add_result = client.call_tool("memory_add", {
        "group_id": cfg.get("group_id", "allura-system"),
        "user_id": cfg.get("agent_id", "hermes-agent"),
        "content": f"PLUGIN_TEST: {token} — Hermes Allura Brain provider round-trip.",
        "metadata": {"source": "manual", "agent_id": "hermes-cli"},
    })
    print(f"  add result: {json.dumps(add_result)[:200]}")
    print(f"Searching for: {token}")
    search_result = client.call_tool("memory_search", {
        "query": token,
        "group_id": cfg.get("group_id", "allura-system"),
        "limit": 3,
    })
    results = search_result.get("results", [])
    found = any(token in r.get("content", "") for r in results)
    print(f"  search returned {len(results)} result(s); token found: {found}")
    print("PASS" if found else "FAIL: token not found in search results")


def my_command(args) -> None:
    """Handler dispatched by argparse."""
    sub = getattr(args, "allura_brain_command", None)
    if sub == "status":
        _cmd_status(args)
    elif sub == "config":
        _cmd_config(args)
    elif sub == "test":
        _cmd_test(args)
    else:
        print("Usage: hermes allura-brain <status|config|test>")


def register_cli(subparser) -> None:
    """Build the `hermes allura-brain` argparse tree."""
    subs = subparser.add_subparsers(dest="allura_brain_command")
    subs.add_parser("status", help="Show provider status and reachability")
    subs.add_parser("config", help="Show current config")
    subs.add_parser("test", help="Round-trip add+search test")
    subparser.set_defaults(func=my_command)