#!/usr/bin/env python3
"""Read-only model inheritance audit and honest benchmark planning (stdlib only)."""
import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
RUNTIMES = ("claude", "opencode", "codex")
LAYOUTS = {
    "claude": ("agents/*.md", ".claude/agents/*.md", ".claude-plugin/agents/*.md"),
    "opencode": (".opencode/agent/**/*.md",),
    "codex": (".codex/agents/*.toml",),
}


def model_binding(path):
    content = path.read_text()
    if path.suffix == ".toml":
        return tomllib.loads(content).get("model")
    frontmatter = re.match(r"\A---\s*\n(.*?)\n---(?:\n|$)", content, re.S)
    if not frontmatter:
        raise ValueError(f"missing agent frontmatter: {path}")
    fields = re.findall(r"^model:\s*([^\n]*)", frontmatter.group(1), re.M)
    if len(fields) > 1:
        raise ValueError(f"duplicate model binding: {path}")
    return fields[0].split(" #", 1)[0].strip().strip("\"'") if fields else None


def audit(root, runtime=None, agent=None):
    rows = []
    for plugin in sorted(root.iterdir()):
        if not plugin.is_dir() or not (plugin / "SOURCE.json").is_file():
            continue
        for host in (runtime,) if runtime else RUNTIMES:
            for pattern in LAYOUTS[host]:
                for path in sorted(plugin.glob(pattern)):
                    if path.name in {"README.md", "BRAIN-CONNECTION.md"}:
                        continue
                    if agent and path.stem != agent:
                        continue
                    # Never follow a generated symlink outside the selected catalog.
                    if not path.resolve().is_relative_to(root.resolve()):
                        raise ValueError(f"agent escapes catalog: {path}")
                    binding = model_binding(path)
                    inherited = binding in (None, "inherit") if host == "claude" else binding is None
                    rows.append({"file": str(path.relative_to(root)), "runtime": host,
                                 "agent": path.stem, "model": binding,
                                 "status": "inherited" if inherited else "drift"})
    if not rows:
        raise ValueError("no matching source-owned agent surfaces; check runtime/agent selectors")
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("audit", "eval", "performance"))
    parser.add_argument("agent", nargs="?", help="exact agent name")
    parser.add_argument("--agent", dest="agent_option", help="exact agent name")
    parser.add_argument("--runtime", choices=RUNTIMES, help="host adapter to inspect")
    parser.add_argument("--dry-run", action="store_true", help="read-only audit or benchmark plan only")
    parser.add_argument("--root", type=Path, default=ROOT, help="catalog root (read-only)")
    args = parser.parse_intermixed_args(argv)
    if args.agent and args.agent_option:
        parser.error("specify the agent only once")
    agent = args.agent or args.agent_option
    try:
        if args.operation == "audit":
            rows = audit(args.root, args.runtime, agent)
            drift = sum(row["status"] == "drift" for row in rows)
            print(json.dumps({"status": "drift" if drift else "passed", "read_only": True,
                              "checked": len(rows), "drift": drift, "agents": rows,
                              "next_action": "Change the canonical source registry/agent, validate, commit, pin source-locks.json and regenerate; never edit generated exports or installed caches."}, indent=2))
            return 1 if drift else 0
        # These commands deliberately do not invoke models or invent Brain telemetry.
        print(json.dumps({"status": "not-run", "operation": args.operation,
                          "agent": agent, "runtime": args.runtime,
                          "measurements": None,
                          "reason": "No benchmark execution or telemetry collection backend is configured by this catalog.",
                          "plan": ["Select representative fixtures and fixed acceptance criteria.",
                                   "Run baseline and candidate with the same tool permissions, tenant, task class and context revision.",
                                   "Record actual configured model, source commit, runtime, retries, elapsed time and validation evidence.",
                                   "Use accepted outcomes and observed cost; missing prices or measurements remain unknown.",
                                   "Review differences before changing source-owned model bindings."]}, indent=2))
        return 0 if args.dry_run else 2
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"model policy error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
