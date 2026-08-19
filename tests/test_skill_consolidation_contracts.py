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

    def test_successor_guidance_remains_owned_by_retained_skills(self) -> None:
        architecture = (SKILL_ROOT / "architecture-patterns" / "references" / "clean-boundaries.md").read_text(encoding="utf-8")
        standards = (SKILL_ROOT / "development-standards" / "SKILL.md").read_text(encoding="utf-8")
        logging = (SKILL_ROOT / "logging-standards" / "references" / "security-and-audit-logging.md").read_text(encoding="utf-8")
        self.assertIn("dependency direction", architecture.lower())
        self.assertIn("repository-owned quality gates", standards.lower())
        self.assertIn("tamper evidence", logging.lower())
