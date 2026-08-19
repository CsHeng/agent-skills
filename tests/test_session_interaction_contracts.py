"""Contract tests for bounded session-interaction skill behavior."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
STRESS_TEST_PATH = (
    REPO_ROOT / "skills/design-change/references/stress-test-mode.md"
)
SESSION_SKILL_PATH = REPO_ROOT / "skills/use-coding-skills/SKILL.md"
PHASE_BOUNDARY_PATH = (
    REPO_ROOT
    / "skills/use-coding-skills/references/phase-boundary-decision-tree.md"
)
ROUTING_PATH = (
    REPO_ROOT / "skills/use-coding-skills/references/routing.toml"
)


def read_text(path: Path) -> str:
    """Read one repository-owned UTF-8 contract file."""

    return path.read_text(encoding="utf-8")


class FrontierRoundContractTests(unittest.TestCase):
    def test_frontier_contract_replaces_the_sequential_default(self) -> None:
        text = read_text(STRESS_TEST_PATH)

        self.assertNotIn("Ask one decision-changing question at a time.", text)
        self.assertIn("## Frontier Contract", text)
        for field in (
            "`frontier`",
            "`round`",
            "`question_id`",
            "`recommendation`",
            "`tradeoff`",
            "`fact_owner`",
            "`sequential_override`",
            "`completion`",
        ):
            self.assertIn(field, text)

    def test_frontier_contract_keeps_dependency_and_completion_order(self) -> None:
        text = read_text(STRESS_TEST_PATH)

        for marker in (
            "prerequisites",
            "whole current frontier",
            "Recompute the frontier",
            "`completion`",
        ):
            self.assertIn(marker, text)

        prerequisite_position = text.index("prerequisites")
        whole_frontier_position = text.index("whole current frontier")
        recompute_position = text.index("Recompute the frontier")
        completion_position = text.index("`completion`")

        self.assertLess(prerequisite_position, whole_frontier_position)
        self.assertLess(whole_frontier_position, recompute_position)
        self.assertLess(recompute_position, completion_position)
        self.assertRegex(text, r"stable `Q\*` identifiers")
        self.assertIn("confirmed assumptions", text)
        self.assertIn("verification and recovery implications", text)


class PhaseBoundaryContractTests(unittest.TestCase):
    def test_session_skill_points_directly_to_the_phase_boundary_reference(
        self,
    ) -> None:
        skill_text = read_text(SESSION_SKILL_PATH)

        self.assertIn(
            "references/phase-boundary-decision-tree.md",
            skill_text,
        )

    def test_phase_boundary_tree_has_the_approved_first_applicable_order(
        self,
    ) -> None:
        self.assertTrue(
            PHASE_BOUNDARY_PATH.is_file(),
            "phase-boundary decision-tree reference is missing",
        )
        text = read_text(PHASE_BOUNDARY_PATH)
        branches = re.findall(r"^### (PB[1-5]) - (.+)$", text, flags=re.MULTILINE)

        self.assertEqual(
            [
                ("PB1", "Continue"),
                ("PB2", "Discard Irrelevant Context"),
                ("PB3", "Portable Handoff"),
                ("PB4", "Policy-Permitted Delegation"),
                ("PB5", "Compact Fallback"),
            ],
            branches,
        )
        self.assertIn("first applicable branch", text)
        self.assertIn("## Entry Condition", text)
        self.assertIn("completed phase boundary", text)
        self.assertIn("Compact Instructions", text)

    def test_phase_boundary_tree_stays_provider_and_policy_neutral(self) -> None:
        self.assertTrue(
            PHASE_BOUNDARY_PATH.is_file(),
            "phase-boundary decision-tree reference is missing",
        )
        text = read_text(PHASE_BOUNDARY_PATH)

        self.assertNotIn("/compact", text)
        self.assertNotIn("/clear", text)
        self.assertIsNone(re.search(r"\b\d{2,3}[kK]\s+tokens\b", text))
        self.assertIn("approved execution policy permits delegation", text)
        self.assertIn("does not authorize delegation", text)

    def test_existing_session_boundary_trigger_owner_is_unchanged(self) -> None:
        with ROUTING_PATH.open("rb") as handle:
            routing = tomllib.load(handle)

        session_case = next(
            case
            for case in routing["trigger_cases"]
            if case["id"] == "session-boundary-handoff"
        )
        self.assertEqual("use-coding-skills", session_case["owner"])


if __name__ == "__main__":
    unittest.main()
