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
        routing_id, routing_entry = next(
            (skill_id, entry)
            for skill_id, entry in cls.contract["skills"].items()
            if entry.get("routing_contract")
        )
        with (SKILL_ROOT / routing_id / routing_entry["routing_contract"]).open("rb") as handle:
            cls.routing = tomllib.load(handle)

    def test_compatibility_skills_are_deleted_from_contract_tree_and_routing(self) -> None:
        routed = set()
        for cluster in self.routing["clusters"]:
            routed.update(cluster["members"])
            for handoff in cluster.get("handoffs", []):
                routed.add(handoff["owner"])
                routed.update(handoff["instead_of"])
        routed_ids = {target.partition(":")[0] for target in routed}
        self.assertFalse(RETIRED & set(self.contract["skills"]))
        self.assertFalse(RETIRED & {path.name for path in SKILL_ROOT.glob("*/")})
        self.assertFalse(RETIRED & routed_ids)
