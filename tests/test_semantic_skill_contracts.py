from __future__ import annotations

import copy
import importlib.util
import tomllib
import unittest
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "check_contracts", REPO_ROOT / "scripts/check-contracts.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load scripts/check-contracts.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract() -> dict[str, object]:
    with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
        return tomllib.load(handle)


class SemanticSkillContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.checker = load_checker()

    def test_current_semantic_contract_is_valid(self) -> None:
        self.assertEqual(
            [], self.checker.validate_semantic_contracts(load_contract(), REPO_ROOT)
        )

    def test_unknown_dependency_is_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["design-change"]["semantic_requires"] = ["missing"]

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("unknown skill: missing" in error for error in errors))

    def test_cycle_is_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["design-change"]["semantic_requires"] = ["plan-change"]
        contract["skills"]["plan-change"]["semantic_requires"] = ["design-change"]

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("contains a cycle" in error for error in errors))

    def test_router_requirements_must_match_installed_routing_contract(self) -> None:
        contract = copy.deepcopy(load_contract())
        routing_entry = next(
            entry
            for entry in contract["skills"].values()
            if entry.get("routing_contract")
        )
        routing_entry["semantic_requires"].remove("output-styles")

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("must match routing targets" in error for error in errors))

    def test_review_evaluators_are_not_mandatory_dependencies(self) -> None:
        contract = load_contract()
        required = contract["skills"]["review-change"].get("semantic_requires", [])
        self.assertTrue(
            {"review-design", "review-plan", "review-implementation"}.isdisjoint(required)
        )

    def test_review_component_evaluators_cannot_delegate(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["review-design"]["may_spawn_agent"] = True

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("cannot delegate" in error for error in errors))

    def test_review_component_evaluators_stay_read_only(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["review-plan"]["may_mutate_repo"] = True

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("read-only" in error for error in errors))

    def test_review_components_declare_non_delegating_metadata(self) -> None:
        contract = load_contract()
        for skill_name in ("review-design", "review-implementation", "review-plan"):
            self.assertFalse(contract["skills"][skill_name]["may_spawn_agent"])
            self.assertFalse(contract["skills"][skill_name]["may_mutate_repo"])

    def test_review_change_keeps_its_own_delegation_ability(self) -> None:
        contract = load_contract()
        self.assertTrue(contract["skills"]["review-change"]["may_spawn_agent"])
        self.assertEqual(
            [], self.checker.validate_semantic_contracts(contract, REPO_ROOT)
        )

    def test_delegation_profile_vocabulary_is_provider_neutral(self) -> None:
        path = (
            REPO_ROOT
            / "skills/plan-change/references/delegation-profiles.toml"
        )
        with path.open("rb") as handle:
            vocabulary = tomllib.load(handle)

        self.assertEqual(1, vocabulary["semantic_vocabulary_version"])
        self.assertFalse(vocabulary["runtime_contract"])
        self.assertEqual(
            ["fast", "balanced", "deep"], vocabulary["execution_profiles"]
        )
        self.assertEqual(
            ["light", "standard", "deep"], vocabulary["reasoning_profiles"]
        )
        self.assertEqual(
            {
                "repository_owner",
                "write_set",
                "resource_locks",
                "isolation",
                "convergence_owner",
                "verification",
                "done_when",
                "failure_policy",
            },
            set(vocabulary["delegation_ready_facts"]),
        )
        self.assertEqual(
            {
                "provider",
                "model",
                "thinking_level",
                "tool_arguments",
                "working_directory_flag",
                "scheduler_limit",
                "retry_count",
                "actor_binding",
                "attempt_state",
                "session_state",
            },
            set(vocabulary["forbidden_binding_keys"]),
        )

    def test_planning_semantics_do_not_grant_spawn_authority(self) -> None:
        contract = load_contract()
        self.assertFalse(contract["skills"]["plan-change"]["may_spawn_agent"])
        self.assertTrue(contract["skills"]["implement-change"]["may_spawn_agent"])


if __name__ == "__main__":
    unittest.main()
