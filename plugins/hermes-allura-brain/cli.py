"""CLI importable through Hermes' synthetic memory-provider package shell."""
from __future__ import annotations

import json

from .client import AlluraBrainClient, checked_result
from .config import load_config as _load_cli_config, secret_headers as _cli_headers


def _client():
    config = _load_cli_config()
    return config, AlluraBrainClient(
        url=config["brain_url"], headers=_cli_headers(config["group_id"]),
        timeout=float(config["timeout"]),
    )


def _status() -> int:
    try:
        config, client = _client()
        headers = _cli_headers(config["group_id"])
        print("Allura Brain Memory Provider")
        print(f"  URL:       {config['brain_url']}")
        print(f"  group_id:  {config['group_id']}")
        print("  identity:  authenticated transport")
        print(f"  sync_mode: {config['sync_mode']}")
        print(f"  secrets:   {json.dumps({key: bool(value) for key, value in headers.items()}, sort_keys=True)}")
        reachable = client.is_reachable()
        print(f"  MCP:       {'CONNECTED' if reachable else 'UNREACHABLE'}")
        return 0 if reachable else 1
    except Exception:
        print("FAIL: invalid profile configuration or MCP status unavailable")
        return 1


def _test() -> int:
    try:
        config, client = _client()
        result = checked_result(client.call_tool("memory_search", {
            "query": "Allura plugin decisions blockers outcomes",
            "group_id": config["group_id"], "limit": 1,
            "status": "all", "include_global": False,
        }))
        rows = result.get("results")
        if not isinstance(rows, list):
            raise RuntimeError("Expected a search results list")
        print(f"Authenticated search completed; results={len(rows)}")
        print("PASS")
        return 0
    except Exception:
        # No response bodies or credential-bearing exceptions in terminal output.
        print("FAIL: authenticated scoped search did not succeed")
        return 1


def allura_brain_command(args) -> None:
    command = getattr(args, "allura_brain_command", None)
    if command == "status":
        raise SystemExit(_status())
    if command == "config":
        try:
            config = _load_cli_config()
            safe = {key: config[key] for key in ("brain_url", "group_id", "sync_mode", "timeout")}
            print(json.dumps(safe, indent=2, sort_keys=True))
        except Exception:
            print("FAIL: invalid Allura Brain profile configuration")
            raise SystemExit(1)
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
