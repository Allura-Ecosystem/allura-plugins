#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path


REQUIRED = [
    "from_runtime",
    "to_runtime",
    "goal",
    "context_searched",
    "project_overlay",
    "files",
    "decisions",
    "open_risks",
    "validation",
    "next_action",
    "memory_status",
    "approval_needed",
]

RUNTIMES = {"Claude", "Codex", "OpenCode", "OpenClaw", "Other"}
TO_RUNTIMES = RUNTIMES | {"None"}
OVERLAYS = {"Team RAM", "Durham", "TALON", "IRIS", "None", "Unknown", "Other"}
CONTEXT_STATUS = {"searched", "unavailable", "not_needed"}
VALIDATION_STATUS = {"passed", "failed", "partial", "not_run"}
MEMORY_STATUS = {"written", "not_written", "unavailable"}
GROUP_RE = re.compile(r"^allura-[a-z0-9-]+$")


def expect(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def validate(packet: dict) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED:
        expect(key in packet, errors, f"missing required field: {key}")
    if errors:
        return errors

    expect(packet["from_runtime"] in RUNTIMES, errors, "invalid from_runtime")
    expect(packet["to_runtime"] in TO_RUNTIMES, errors, "invalid to_runtime")
    expect(isinstance(packet["goal"], str) and bool(packet["goal"].strip()), errors, "goal must be non-empty string")
    expect(packet["project_overlay"] in OVERLAYS, errors, "invalid project_overlay")
    expect(isinstance(packet["next_action"], str) and bool(packet["next_action"].strip()), errors, "next_action must be non-empty string")

    context = packet["context_searched"]
    expect(isinstance(context, dict), errors, "context_searched must be object")
    if isinstance(context, dict):
        expect(context.get("status") in CONTEXT_STATUS, errors, "invalid context_searched.status")
        group_id = context.get("group_id")
        if group_id is not None:
            expect(isinstance(group_id, str) and bool(GROUP_RE.match(group_id)), errors, "group_id must match ^allura-[a-z0-9-]+$")
        expect("queries" not in context or string_list(context["queries"]), errors, "context_searched.queries must be list of strings")
        expect("memory_ids" not in context or string_list(context["memory_ids"]), errors, "context_searched.memory_ids must be list of strings")
        if context.get("status") == "searched":
            expect(bool(context.get("queries")), errors, "searched context requires at least one query")
        if context.get("status") == "unavailable":
            expect(bool(context.get("reason")), errors, "unavailable context requires reason")

    files = packet["files"]
    expect(isinstance(files, dict), errors, "files must be object")
    if isinstance(files, dict):
        expect(string_list(files.get("read")), errors, "files.read must be list of strings")
        expect(string_list(files.get("changed")), errors, "files.changed must be list of strings")

    expect(string_list(packet["decisions"]), errors, "decisions must be list of strings")
    expect(string_list(packet["open_risks"]), errors, "open_risks must be list of strings")

    validation = packet["validation"]
    expect(isinstance(validation, dict), errors, "validation must be object")
    if isinstance(validation, dict):
        expect(validation.get("status") in VALIDATION_STATUS, errors, "invalid validation.status")
        expect(string_list(validation.get("commands")), errors, "validation.commands must be list of strings")
        expect("evidence_paths" not in validation or string_list(validation["evidence_paths"]), errors, "validation.evidence_paths must be list of strings")
        if validation.get("status") == "passed":
            expect(bool(validation.get("commands") or validation.get("evidence_paths")), errors, "passed validation requires command or evidence path")

    memory = packet["memory_status"]
    expect(isinstance(memory, dict), errors, "memory_status must be object")
    if isinstance(memory, dict):
        expect(memory.get("status") in MEMORY_STATUS, errors, "invalid memory_status.status")
        if memory.get("status") == "written":
            expect(bool(memory.get("memory_id")), errors, "written memory_status requires memory_id")
        if memory.get("status") in {"not_written", "unavailable"}:
            expect(bool(memory.get("reason")) or memory.get("status") == "not_written", errors, "unavailable memory_status requires reason")

    approval = packet["approval_needed"]
    expect(isinstance(approval, dict), errors, "approval_needed must be object")
    if isinstance(approval, dict):
        expect(isinstance(approval.get("required"), bool), errors, "approval_needed.required must be boolean")
        if approval.get("required"):
            expect(bool(approval.get("reason")), errors, "approval_needed.reason required when approval is required")

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate_handoff.py <packet.json> [<packet.json> ...]", file=sys.stderr)
        return 2

    all_errors: dict[str, list[str]] = {}
    for raw in sys.argv[1:]:
        path = Path(raw)
        try:
            packet = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            all_errors[str(path)] = [f"invalid json: {exc}"]
            continue
        if not isinstance(packet, dict):
            all_errors[str(path)] = ["packet root must be object"]
            continue
        errors = validate(packet)
        if errors:
            all_errors[str(path)] = errors

    result = {
        "status": "passed" if not all_errors else "failed",
        "checked": sys.argv[1:],
        "errors": all_errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
