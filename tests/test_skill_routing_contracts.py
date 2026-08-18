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
            self.skill_contract = tomllib.load(handle)
            self.skills = self.skill_contract["skills"]
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
        with source_path.open("rb") as handle:
            self.routing_contract = tomllib.load(handle)

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

    def validate_trigger_cases(
        self,
        routing_contract: dict[str, object] | None = None,
        skills: dict[str, object] | None = None,
    ) -> list[str]:
        return CHECK_CONTRACTS.validate_trigger_cases(
            skills or self.skills,
            routing_contract or self.routing_contract,
        )

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

    def test_code_simplification_owns_read_only_audit_route(self) -> None:
        self.assertIn("code-simplification", self.skills)
        skill = self.skills["code-simplification"]
        self.assertEqual(
            "src/skills/disciplines/code-simplification", skill["source"]
        )
        self.assertEqual("discipline", skill["category"])
        self.assertEqual("native", skill["activation_mode"])
        self.assertEqual("primary", skill["default_role"])
        self.assertFalse(skill["may_mutate_repo"])
        self.assertFalse(skill["may_spawn_agent"])

        router = self.skills["use-coding-skills"]
        self.assertIn("code-simplification", router["semantic_requires"])
        cases = [
            case
            for case in self.routing_contract["trigger_cases"]
            if case["id"] == "code-simplification-audit"
        ]
        self.assertEqual(1, len(cases))
        self.assertEqual("code-simplification", cases[0]["owner"])
        negative_contract = " ".join(cases[0]["negative"]).lower()
        for boundary in ("ordinary", "performance", "apply", "current diff"):
            self.assertIn(boundary, negative_contract)

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

    def test_current_trigger_case_registry_is_complete(self) -> None:
        self.assertEqual([], self.validate_trigger_cases())

    def test_trigger_case_ids_and_owner_are_singular(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        duplicate = copy.deepcopy(routing["trigger_cases"][0])
        duplicate["owner"] = [duplicate["owner"], "analyze-project"]
        routing["trigger_cases"].append(duplicate)

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("duplicate trigger case id" in error for error in errors))
        self.assertTrue(any("exactly one owner" in error for error in errors))

    def test_trigger_cases_require_semantic_positive_and_negative_examples(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        routing["trigger_cases"][0]["positive"] = []
        routing["trigger_cases"][0].pop("negative")
        routing["trigger_cases"][0]["lexical_hints"] = ["architecture"]

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("non-empty positive" in error for error in errors))
        self.assertTrue(any("non-empty negative" in error for error in errors))
        self.assertTrue(any("cannot be keyword-only" in error for error in errors))

    def test_unknown_targets_and_lifecycle_owner_overlays_are_rejected(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        routing["trigger_cases"][0]["owner"] = "missing"
        routing["trigger_cases"][1]["overlays"] = ["design-change"]

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("unknown owner" in error for error in errors))
        self.assertTrue(any("lifecycle owner cannot be an overlay" in error for error in errors))

    def test_controller_evaluators_and_compatibility_helpers_cannot_own_cases(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        routing["trigger_cases"][0]["owner"] = "review-implementation"
        routing["trigger_cases"][1]["owner"] = "clean-architecture"

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("controller evaluator cannot own" in error for error in errors))
        self.assertTrue(any("compatibility helper cannot own" in error for error in errors))

    def test_uncovered_native_skill_is_rejected(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        routing["trigger_cases"] = [
            case
            for case in routing["trigger_cases"]
            if case["owner"] != "analyze-project"
        ]

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("analyze-project: native skill must own" in error for error in errors))

    def test_baseline_must_match_rendering_composition(self) -> None:
        routing = copy.deepcopy(self.routing_contract)
        routing["composition"]["rendering_baseline"] = "use-coding-skills"

        errors = self.validate_trigger_cases(routing)

        self.assertTrue(any("baseline must match composition.rendering_baseline" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
