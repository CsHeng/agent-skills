from __future__ import annotations

import copy
import importlib.util
import tempfile
import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_contracts_routing", REPO_ROOT / "scripts" / "check-contracts.py"
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("failed to load scripts/check-contracts.py")
CHECK_CONTRACTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_CONTRACTS)


class RoutingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            self.skills = tomllib.load(handle)["skills"]
        with (REPO_ROOT / "contracts/workflow-modes.toml").open("rb") as handle:
            self.workflow_modes = tomllib.load(handle)

        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        routing_entry = self.skills["use-coding-skills"]
        self.contract_path = (
            self.root / routing_entry["source"] / routing_entry["routing_contract"]
        )
        self.contract_path.parent.mkdir(parents=True)
        source_path = (
            REPO_ROOT / routing_entry["source"] / routing_entry["routing_contract"]
        )
        self.contract_path.write_text(
            source_path.read_text(encoding="utf-8"), encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def validate(self, skills: dict[str, object] | None = None) -> list[str]:
        return CHECK_CONTRACTS.validate_routing_contracts(
            skills or self.skills,
            self.root,
            self.workflow_modes,
        )

    def rewrite(self, old: str, new: str) -> None:
        current = self.contract_path.read_text(encoding="utf-8")
        self.contract_path.write_text(current.replace(old, new), encoding="utf-8")

    def test_valid_repo_routing_contract(self) -> None:
        self.assertEqual([], self.validate())

    def test_exactly_one_routing_contract_is_required(self) -> None:
        skills = copy.deepcopy(self.skills)
        del skills["use-coding-skills"]["routing_contract"]

        errors = self.validate(skills)

        self.assertTrue(
            any("exactly one routing_contract" in error for error in errors)
        )

    def test_native_direct_match_bypass_is_required(self) -> None:
        self.rewrite(
            "direct_match_bypasses_router = true",
            "direct_match_bypasses_router = false",
        )

        errors = self.validate()

        self.assertTrue(any("native discovery" in error for error in errors))

    def test_every_workflow_mode_phase_requires_a_route(self) -> None:
        self.rewrite('verify = "implement-change"\n', "")

        errors = self.validate()

        self.assertTrue(
            any(
                "phase routes missing workflow phases: verify" in error
                for error in errors
            )
        )

    def test_phase_routes_must_target_lifecycle_owners(self) -> None:
        self.rewrite(
            'execute = "implement-change"', 'execute = "review-implementation"'
        )

        errors = self.validate()

        self.assertTrue(
            any("must route to a lifecycle owner" in error for error in errors)
        )

    def test_gate_policy_must_preserve_implicit_design_and_plan_review(self) -> None:
        self.rewrite(
            "implicit_review_when_missing = true",
            "implicit_review_when_missing = false",
        )

        errors = self.validate()

        self.assertTrue(
            any(
                "must preserve implicit design and plan review" in error
                for error in errors
            )
        )

    def test_review_phases_require_review_component_evaluators(self) -> None:
        self.rewrite('review = "review-implementation"', 'review = "review-change"')

        errors = self.validate()

        self.assertTrue(any("must use a review-component" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
