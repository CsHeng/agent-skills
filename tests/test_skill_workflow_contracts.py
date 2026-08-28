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
        with (
            REPO_ROOT
            / "skills/use-coding-skills/references/routing.toml"
        ).open("rb") as handle:
            cls.routing = tomllib.load(handle)

    def test_obsolete_controller_contracts_are_absent(self) -> None:
        self.assertFalse((REPO_ROOT / "contracts/lifecycle.toml").exists())
        self.assertFalse((REPO_ROOT / "contracts/workflow-modes.toml").exists())
        for table in ("gate_policy", "phase_routes", "review_evaluators"):
            self.assertNotIn(table, self.routing)

    def test_ordinary_workflows_have_no_universal_review_or_plan_gate(self) -> None:
        skills = self.contract["skills"]
        for skill_id in ("design-change", "plan-change", "implement-change"):
            with self.subTest(skill=skill_id):
                self.assertNotIn("semantic_requires", skills[skill_id])
        self.assertTrue(skills["implement-change"]["requires_explicit_user_request"])
        self.assertNotIn("requires_approved_plan", skills["implement-change"])
        self.assertNotIn("semantic_requires", skills["review-change"])

    def test_truth_mutation_uses_explicit_authority_without_synthetic_plan(self) -> None:
        skills = self.contract["skills"]
        for skill_id in ("sync-truth", "organize-docs"):
            with self.subTest(skill=skill_id):
                self.assertTrue(skills[skill_id]["requires_explicit_user_request"])
                self.assertNotIn("requires_approved_plan", skills[skill_id])

    def test_explicit_herdr_delegation_retains_frozen_plan_scope(self) -> None:
        herdr = self.contract["skills"]["implement-change-via-herdr"]
        self.assertTrue(herdr["requires_explicit_user_request"])
        self.assertTrue(herdr["requires_approved_plan"])
        self.assertEqual(["implement-change"], herdr["semantic_requires"])

    def test_review_evaluators_are_optional_composition_capabilities(self) -> None:
        skills = self.contract["skills"]
        for skill_id in ("review-design", "review-plan", "review-implementation"):
            with self.subTest(skill=skill_id):
                self.assertEqual("composition", skills[skill_id]["activation_mode"])
                self.assertEqual("evaluator", skills[skill_id]["default_role"])
                self.assertNotIn("semantic_requires", skills[skill_id])

    def test_skills_do_not_publish_runtime_contracts(self) -> None:
        for skill_id, entry in self.contract["skills"].items():
            with self.subTest(skill=skill_id):
                self.assertNotIn("runtime_contract", entry)
                self.assertNotIn("runtime_bundle", entry)
                self.assertNotIn("lifecycle_owner", entry)


if __name__ == "__main__":
    unittest.main()
