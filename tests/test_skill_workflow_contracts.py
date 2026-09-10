from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHORED_DESIGN = REPO_ROOT / "src/skills/workflows/design-change/SKILL.md"
AUTHORED_GOAL_ALIGNMENT = (
    REPO_ROOT / "src/skills/workflows/design-change/references/goal-alignment.md"
)
AUTHORED_PLAN = REPO_ROOT / "src/skills/workflows/plan-change/SKILL.md"
AUTHORED_DELIVERY = (
    REPO_ROOT / "src/skills/workflows/plan-change/references/delivery-and-delegation.md"
)
AUTHORED_IMPLEMENT = REPO_ROOT / "src/skills/workflows/implement-change/SKILL.md"
INVOCATION_CONTRACT = REPO_ROOT / "docs/architecture/invocation-contract.md"


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            cls.contract = tomllib.load(handle)
        with (REPO_ROOT / "skills/use-coding-skills/references/routing.toml").open(
            "rb"
        ) as handle:
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

    def test_truth_mutation_uses_explicit_authority_without_synthetic_plan(
        self,
    ) -> None:
        skills = self.contract["skills"]
        for skill_id in ("sync-truth", "organize-docs"):
            with self.subTest(skill=skill_id):
                self.assertTrue(skills[skill_id]["requires_explicit_user_request"])
                self.assertNotIn("requires_approved_plan", skills[skill_id])

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

    def test_delivery_consideration_does_not_imply_authority(self) -> None:
        design = AUTHORED_DESIGN.read_text(encoding="utf-8")
        alignment = AUTHORED_GOAL_ALIGNMENT.read_text(encoding="utf-8")
        plan = AUTHORED_PLAN.read_text(encoding="utf-8")
        delivery = AUTHORED_DELIVERY.read_text(encoding="utf-8")
        invocation = INVOCATION_CONTRACT.read_text(encoding="utf-8")

        for text in (design, alignment, delivery, invocation):
            with self.subTest(surface="endpoint"):
                self.assertIn("useful delivery endpoint", text)
        self.assertIn("existing-environment deploy", alignment)
        self.assertIn("post-deploy verification", alignment)
        self.assertIn("publish, install, or handoff", alignment)
        self.assertIn(
            "current activity is planning-only",
            plan,
        )
        self.assertIn("Planning does not grant authority", plan)
        self.assertIn("not default operational permission", alignment)
        self.assertIn("not operational permission", plan)
        self.assertIn("source-only or design-only", alignment)
        self.assertIn("source-only or design-only", plan)
        self.assertIn("without granting operational permission", invocation)

    def test_plan_approval_summary_classifies_gates(self) -> None:
        plan = AUTHORED_PLAN.read_text(encoding="utf-8")
        delivery = AUTHORED_DELIVERY.read_text(encoding="utf-8")
        invocation = INVOCATION_CONTRACT.read_text(encoding="utf-8")

        for text in (plan, delivery, invocation):
            with self.subTest(surface="classified-gates"):
                self.assertIn("may approve together", text)
                self.assertIn("already covered", text.lower())
                self.assertIn("must execute", text)
                self.assertIn("manual checkpoints", text.lower())
        self.assertIn("**Agent-owned execution:**", delivery)
        self.assertIn("Do not ask approval for these.", delivery)
        self.assertIn("not a universal endless-execution engine", delivery)

    def test_later_explicit_delivery_updates_effective_plan(self) -> None:
        implement = AUTHORED_IMPLEMENT.read_text(encoding="utf-8")
        delivery = AUTHORED_DELIVERY.read_text(encoding="utf-8")
        invocation = INVOCATION_CONTRACT.read_text(encoding="utf-8")

        for text in (implement, delivery):
            with self.subTest(surface="effective-plan"):
                self.assertIn("approved, include commit/push/deploy", text)
                self.assertIn("currently effective", text)
                self.assertIn("provenance", text)
                self.assertIn("override sentence", text)
                self.assertIn("document annotation or review success", text)
                self.assertIn("waive required verification", text)
        self.assertIn("currently effective plan", invocation)
        self.assertIn("not a universal execution engine or approval ledger", invocation)

    def test_delivery_policy_does_not_weaken_authority_or_acceptance(self) -> None:
        implement = AUTHORED_IMPLEMENT.read_text(encoding="utf-8")
        plan = AUTHORED_PLAN.read_text(encoding="utf-8")
        design = AUTHORED_DESIGN.read_text(encoding="utf-8")

        self.assertIn(
            "need matching authority, not merely implementation approval",
            implement,
        )
        self.assertIn(
            "review success does not authorize implementation",
            plan,
        )
        self.assertIn(
            "Do not mark a design approved from review success alone",
            design,
        )
        self.assertIn("Never weaken assertions", implement)
        self.assertNotIn("requires_approved_plan", plan)
        self.assertNotIn("approval protocol", implement)
        self.assertNotIn("runtime engine", implement)


if __name__ == "__main__":
    unittest.main()
