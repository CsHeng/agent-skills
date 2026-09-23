from __future__ import annotations

import unittest
from pathlib import Path

import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills"
RETIRED = {"clean-architecture", "quality-standards", "security-logging"}


class SkillConsolidationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
            cls.contract = tomllib.load(handle)
        with (SKILL_ROOT / "use-coding-skills" / "references" / "routing.toml").open("rb") as handle:
            cls.routing = tomllib.load(handle)

    def test_compatibility_skills_are_deleted_from_contract_tree_and_routing(self) -> None:
        case_owners = {case["owner"] for case in self.routing["trigger_cases"]}
        self.assertFalse(RETIRED & set(self.contract["skills"]))
        self.assertFalse(RETIRED & {path.name for path in SKILL_ROOT.glob("*/")})
        self.assertFalse(RETIRED & case_owners)
