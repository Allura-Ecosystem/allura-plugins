"""Native Hermes registration for CorpLawyer's bundled workflows."""
from pathlib import Path


SKILLS = (
    "instructions",
    "matter-intake",
    "legal-research",
    "contract-review",
    "counsel-brief",
    "allura-continuity",
)


def register(ctx):
    root = Path(__file__).parent / "skills"
    for name in SKILLS:
        ctx.register_skill(name, root / name / "SKILL.md")
