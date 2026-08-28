from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            cls.contract = tomllib.load(handle)

    def skill_text(self, skill_id: str) -> str:
        return (REPO_ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")

    def test_formal_workflows_compose_exactly_one_review(self) -> None:
        for skill_id in ("design-change", "plan-change", "implement-change"):
            with self.subTest(skill=skill_id):
                entry = self.contract["skills"][skill_id]
                self.assertEqual(["review-change"], entry["semantic_requires"])
                text = self.skill_text(skill_id)
                self.assertIn("exactly once", text)
                self.assertIn("without starting another review", text)

    def test_informal_work_does_not_inherit_review(self) -> None:
        for skill_id in ("design-change", "plan-change", "implement-change"):
            with self.subTest(skill=skill_id):
                self.assertIn("informal", self.skill_text(skill_id).lower())

    def test_standalone_review_is_bounded_and_forward_only(self) -> None:
        text = self.skill_text("review-change")
        self.assertIn("needs only a bounded target", text)
        self.assertIn("Do not require or create an upstream design", text)
        self.assertIn("remains read-only", text)
        self.assertIn("must not delegate recursively", text)
        self.assertIn("never performs the repair", text)

    def test_workflow_skills_do_not_publish_runtime_contracts(self) -> None:
        for skill_id, entry in self.contract["skills"].items():
            with self.subTest(skill=skill_id):
                self.assertNotIn("runtime_contract", entry)
                self.assertNotIn("runtime_bundle", entry)

    def test_workflow_text_is_provider_neutral(self) -> None:
        forbidden = (
            "active host",
            "host harness",
            "skill-local lifecycle controller",
            "task ledger",
            "physical model",
            "session replay",
            "parent-linked broker intent",
            "external-baseline",
        )
        for skill_id in (
            "design-change",
            "plan-change",
            "implement-change",
            "review-change",
            "sync-truth",
            "close-change",
        ):
            text = self.skill_text(skill_id).lower()
            for phrase in forbidden:
                with self.subTest(skill=skill_id, phrase=phrase):
                    self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
