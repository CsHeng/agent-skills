from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = REPO_ROOT / "skills/implement-change/references/workflow.toml"
PORTABLE_PLAN_SURFACES = (
    REPO_ROOT / "skills/plan-change/SKILL.md",
    REPO_ROOT / "skills/review-plan/SKILL.md",
    REPO_ROOT / "skills/executable-oracle-architecture-selector/SKILL.md",
    CONTRACTS,
    REPO_ROOT / "src/runtime/harness/artifacts.py",
)
EXTERNAL_TOUCH_POLICY = "exact-existing-files-v1"
CONCRETE_PROVIDER_MODEL = re.compile(
    r"\b(?:gpt-\d|claude-(?:\d|opus|sonnet|haiku)|gemini-(?:\d|pro|flash))",
    re.IGNORECASE,
)


def workflow_contract() -> dict[str, object]:
    with CONTRACTS.open("rb") as handle:
        return tomllib.load(handle)


class ParallelExecutionContractTests(unittest.TestCase):
    def test_portable_plan_contract_uses_semantic_profiles(self) -> None:
        execution = workflow_contract()["execution"]
        self.assertEqual(["deep", "balanced", "fast"], execution["execution_profiles"])
        self.assertEqual(["deep", "standard", "light"], execution["reasoning_profiles"])
        self.assertEqual(
            ["semantic-routing", "inherit-main", "runtime-default"],
            execution["allowed_model_policies"],
        )

    def test_parallel_and_delegation_policies_are_independent(self) -> None:
        plan = PORTABLE_PLAN_SURFACES[0].read_text(encoding="utf-8")
        self.assertIn("parallel_policy", plan)
        self.assertIn("delegation_policy", plan)
        self.assertIn("may conservatively serialize", plan)

    def test_reusable_planning_surfaces_do_not_pin_provider_models(self) -> None:
        violations: list[str] = []
        for file_ref in PORTABLE_PLAN_SURFACES:
            content = file_ref.read_text(encoding="utf-8")
            if CONCRETE_PROVIDER_MODEL.search(content):
                violations.append(str(file_ref.relative_to(REPO_ROOT)))
        self.assertEqual([], violations)

    def test_portable_planning_keeps_difficulty_separate_from_physical_ceiling(self) -> None:
        plan_text = PORTABLE_PLAN_SURFACES[0].read_text(encoding="utf-8")
        self.assertIn("parent", plan_text)
        self.assertIn("minimum", plan_text)
        self.assertIn("no physical reasoning ceiling", plan_text)
        self.assertNotIn("absolute low-cost", plan_text)
        self.assertNotIn("medium as the ceiling", plan_text)

    def test_external_touch_policy_remains_provider_neutral(self) -> None:
        contract_text = CONTRACTS.read_text(encoding="utf-8")
        artifact_compiler = (REPO_ROOT / "src/runtime/harness/artifacts.py").read_text(
            encoding="utf-8"
        )
        self.assertIn(EXTERNAL_TOUCH_POLICY, contract_text)
        self.assertIn("external_impl_file_refs", artifact_compiler)
        self.assertNotRegex(contract_text, CONCRETE_PROVIDER_MODEL)


if __name__ == "__main__":
    unittest.main()
