from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from types import ModuleType

import tomllib

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
        contract["skills"]["design-change"]["semantic_requires"].append("missing")

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("unknown skill: missing" in error for error in errors))

    def test_cycle_is_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["close-change"]["semantic_requires"] = [
            "implement-change"
        ]

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("contains a cycle" in error for error in errors))

    def test_router_requirements_must_match_installed_routing_contract(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["use-coding-skills"]["semantic_requires"].remove(
            "output-styles"
        )

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(any("must match routing targets" in error for error in errors))

    def test_runtime_edge_requires_semantic_declaration(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["review-change"]["semantic_requires"].remove(
            "review-implementation"
        )

        errors = self.checker.validate_semantic_contracts(contract, REPO_ROOT)

        self.assertTrue(
            any("runtime edge lacks semantic_requires" in error for error in errors)
        )


if __name__ == "__main__":
    unittest.main()
