"""Structural checks for installed session references and routing ownership."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PHASE_BOUNDARY_REFERENCE = "references/phase-boundary-decision-tree.md"


class SessionSurfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            skills = tomllib.load(handle)["skills"]
        cls.routing_id, routing_entry = next(
            (skill_id, entry)
            for skill_id, entry in skills.items()
            if entry.get("routing_contract")
        )
        cls.skill_root = REPO_ROOT / "skills" / cls.routing_id
        cls.routing_path = cls.skill_root / routing_entry["routing_contract"]

    def test_session_skill_references_the_phase_boundary_document(self) -> None:
        skill_text = (self.skill_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(PHASE_BOUNDARY_REFERENCE, skill_text)

    def test_installed_session_references_exist(self) -> None:
        paths = (
            self.skill_root / PHASE_BOUNDARY_REFERENCE,
            REPO_ROOT / "skills/design-change/references/stress-test-mode.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertTrue(path.is_file())

    def test_session_boundary_trigger_belongs_to_the_router(self) -> None:
        with self.routing_path.open("rb") as handle:
            routing = tomllib.load(handle)

        session_case = next(
            case
            for case in routing["trigger_cases"]
            if case["id"] == "session-boundary-handoff"
        )
        self.assertEqual(self.routing_id, session_case["owner"])


if __name__ == "__main__":
    unittest.main()
