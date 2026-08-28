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
        contract["skills"]["use-coding-skills"]["semantic_requires"].remove(
            "output-styles"
        )

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("must match routing targets" in error for error in errors))

    def test_review_evaluators_are_not_mandatory_dependencies(self) -> None:
        contract = load_contract()
        self.assertNotIn("semantic_requires", contract["skills"]["review-change"])


if __name__ == "__main__":
    unittest.main()
