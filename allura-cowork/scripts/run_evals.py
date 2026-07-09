#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    cases_path = root / "evals/cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    corpus_paths = [
        root / "skills/allura-cowork/SKILL.md",
        root / "commands/cowork-start.md",
        root / "commands/cowork-handoff.md",
        root / "commands/cowork-validate.md",
        root / "commands/cowork-close.md",
        root / "docs/COMMAND-MENU.md",
        root / "docs/EVALS.md",
    ]
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in corpus_paths)
    corpus_lower = corpus.lower()

    errors = []
    for case in cases:
        case_id = case.get("id", "<missing>")
        if case.get("expected_status") not in {"PASS", "WATCH", "BLOCKED"}:
            errors.append(f"{case_id}: invalid expected_status")
        guardrails = case.get("expected_guardrails")
        if not isinstance(guardrails, list) or not guardrails:
            errors.append(f"{case_id}: expected_guardrails must be non-empty list")
            continue
        missing = [item for item in guardrails if str(item).lower() not in corpus_lower]
        if missing:
            errors.append(f"{case_id}: guardrails missing from docs: {missing}")

    result = {
        "status": "passed" if not errors else "failed",
        "cases": len(cases),
        "errors": errors,
    }
    print(json.dumps(result, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
