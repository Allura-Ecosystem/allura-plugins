"""Native Hermes registration for Prompt Optimization Bot."""
from pathlib import Path


def register(ctx):
    ctx.register_skill("instructions", Path(__file__).parent / "skills" / "instructions" / "SKILL.md")
