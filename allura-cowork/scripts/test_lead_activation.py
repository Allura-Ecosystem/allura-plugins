"""Offline menu selection and continuity contracts; no model behavior asserted."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class LeadActivationTests(unittest.TestCase):
    def test_shared_menu_defers_to_the_selected_lead(self):
        menu = (ROOT / "skills/allura-menu/SKILL.md").read_text()
        for term in ("Brooks or Kotler", "loaded full role", "domain menu", "under More",
                     "quoted mentions", "follow-ups and compaction", "without another confirmation"):
            self.assertIn(term, menu)
        for choice in ("Next steps", "Help with a prompt", "Council", "Work", "Loop", "Validate", "More"):
            self.assertIn(f"- {choice} —", menu)

    def test_entry_preserves_scoped_truthful_reflections(self):
        entry = (ROOT / "skills/allura-cowork/SKILL.md").read_text()
        for term in ("full installed role", "main conversation", "compaction", "one bounded query",
                     "memory ID/date", "current judgment", "no relevant memory", "pending",
                     "unavailable retrieval", "Do not invent continuity or write startup chatter"):
            self.assertIn(term, entry)


if __name__ == "__main__":
    unittest.main()
