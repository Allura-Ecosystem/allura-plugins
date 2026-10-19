"""Shared profile configuration and tenant-bound credentials; no network I/O."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
from typing import Any

from agent.secret_scope import get_secret

PUBLIC_BRAIN_URL = "https://mcp.faithmeats.org/mcp"
LEGACY_PREFIXES = ("allura-roninmemory", "allura-team-ram")


def validate_group_id(value: Any) -> str:
    if not isinstance(value, str) or re.fullmatch(r"allura-[a-z0-9-]+", value) is None:
        raise ValueError("An explicit group_id matching ^allura-[a-z0-9-]+$ is required")
    if value.startswith(LEGACY_PREFIXES):
        raise ValueError("Retired Allura tenant is blocked")
    return value


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    validate_group_id(config.get("group_id"))
    if config.get("brain_url") != PUBLIC_BRAIN_URL:
        raise ValueError("Allura Brain provider refuses non-canonical endpoint")
    if config.get("sync_mode") not in ("off", "outcomes_only", "full"):
        raise ValueError("sync_mode must be off, outcomes_only, or full")
    timeout = float(config.get("timeout", 30))
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a positive finite number")
    return config


def load_config(hermes_home: str | None = None, *, values: dict | None = None) -> dict:
    home = Path(hermes_home or os.environ.get("HERMES_HOME") or Path.home() / ".hermes")
    config = {"brain_url": PUBLIC_BRAIN_URL, "sync_mode": "outcomes_only", "timeout": 30.0}
    path = home / "allura-brain.json"
    if path.exists():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(loaded, dict):
            raise ValueError("allura-brain.json must be a JSON object")
        config.update(loaded)
    if values is not None:
        config.update(values)
    # Historical agent_id is retained on disk but has no authority or transport use.
    return validate_config(config)


def secret_headers(group_id: str) -> dict[str, str]:
    group_id = validate_group_id(group_id)
    bearer = get_secret("ALLURA_MCP_TOKEN", "").strip()
    alias = {
        "allura-system": "ALLURA_MCP_TROY_DESKTOP_TOKEN",
        "allura-faithmeats": "ALLURA_MCP_TROY_ADMIN_TOKEN",
    }.get(group_id)
    if not bearer and alias:
        bearer = get_secret(alias, "").strip()
    headers = {}
    for key, value in (
        ("Authorization", f"Bearer {bearer}" if bearer else ""),
        ("CF-Access-Client-Id", get_secret("ALLURA_CF_ACCESS_CLIENT_ID", "").strip()),
        ("CF-Access-Client-Secret", get_secret("ALLURA_CF_ACCESS_CLIENT_SECRET", "").strip()),
    ):
        if value:
            headers[key] = value
    return headers
