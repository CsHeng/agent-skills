from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = REPO_ROOT / "src/runtime/harness/contracts.sh"
PORTABLE_PLAN_SURFACES = (
    REPO_ROOT / "src/skills/workflows/plan-change/SKILL.md",
    REPO_ROOT / "src/skills/review-components/review-plan/SKILL.md",
    REPO_ROOT / "src/skills/disciplines/executable-oracle-architecture-selector/SKILL.md",
    CONTRACTS,
    REPO_ROOT / "src/runtime/harness/plan-runner.sh",
)
EXTERNAL_TOUCH_POLICY = "exact-existing-files-v1"
CONCRETE_PROVIDER_MODEL = re.compile(
    r"\b(?:gpt-\d|claude-(?:\d|opus|sonnet|haiku)|gemini-(?:\d|pro|flash))",
    re.IGNORECASE,
)


def contract_values(array_name: str) -> list[str]:
    script = 'source "$1"; declare -n selected_values="$2"; printf "%s\\n" "${selected_values[@]}"'
    result = subprocess.run(
        ["bash", "-c", script, "parallel-contract-test", str(CONTRACTS), array_name],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.splitlines()


class ParallelExecutionContractTests(unittest.TestCase):
    def test_portable_plan_contract_uses_semantic_profiles(self) -> None:
        self.assertEqual(["deep", "balanced", "fast"], contract_values("HARNESS_EXECUTION_PROFILES"))
        self.assertEqual(["deep", "standard", "light"], contract_values("HARNESS_REASONING_PROFILES"))
        self.assertEqual(
            ["semantic-routing", "inherit-main", "runtime-default"],
            contract_values("HARNESS_MODEL_POLICIES"),
        )

    def test_parallel_and_delegation_policies_are_independent(self) -> None:
        self.assertEqual(["forbidden", "allowed", "required"], contract_values("HARNESS_PARALLEL_POLICIES"))
        self.assertEqual(
            ["forbidden", "allowed", "preferred"],
            contract_values("HARNESS_DELEGATION_POLICIES"),
        )

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
        plan_runner = (REPO_ROOT / "src/runtime/harness/plan-runner.sh").read_text(encoding="utf-8")
        artifact_dag = (REPO_ROOT / "src/runtime/harness/artifact-dag.sh").read_text(encoding="utf-8")
        self.assertIn(EXTERNAL_TOUCH_POLICY, plan_runner)
        self.assertIn("external_impl_file_refs", artifact_dag)
        self.assertNotRegex(plan_runner, CONCRETE_PROVIDER_MODEL)


if __name__ == "__main__":
    unittest.main()
