"""Structural checks for installed session references and routing ownership."""

from __future__ import annotations

import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_SKILL_ROOT = REPO_ROOT / "skills/use-coding-skills"
PHASE_BOUNDARY_REFERENCE = "references/phase-boundary-decision-tree.md"


class SessionSurfaceContractTests(unittest.TestCase):
    def test_session_skill_references_the_phase_boundary_document(self) -> None:
        skill_text = (SESSION_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn(PHASE_BOUNDARY_REFERENCE, skill_text)

    def test_installed_session_references_exist(self) -> None:
        paths = (
            SESSION_SKILL_ROOT / PHASE_BOUNDARY_REFERENCE,
            REPO_ROOT / "skills/design-change/references/stress-test-mode.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(REPO_ROOT)):
                self.assertTrue(path.is_file())

    def test_existing_session_boundary_trigger_owner_is_unchanged(self) -> None:
        with (SESSION_SKILL_ROOT / "references/routing.toml").open("rb") as handle:
            routing = tomllib.load(handle)

        session_case = next(
            case
            for case in routing["trigger_cases"]
            if case["id"] == "session-boundary-handoff"
        )
        self.assertEqual("use-coding-skills", session_case["owner"])


if __name__ == "__main__":
    unittest.main()
