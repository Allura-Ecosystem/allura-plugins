"""Native Hermes registration for Team Durham App Audit."""
from pathlib import Path


def register(ctx):
    ctx.register_skill("app-audit", Path(__file__).parent / "skills" / "app-audit" / "SKILL.md")
