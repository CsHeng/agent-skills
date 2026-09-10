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

    def test_instruction_scope_separates_preferences_records_and_methods(self) -> None:
        instructions = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        scope = instructions.split("## Instruction Scope\n", 1)[1].split("\n## ", 1)[0]

        for concern in (
            "Harness-global instructions",
            "persistent user preferences",
            "Project `AGENTS.md`",
            "current design, plan, or approval summary",
            "Skills own portable workflow and domain methods",
            "separately approved scope",
        ):
            with self.subTest(concern=concern):
                self.assertIn(concern, scope)

    def test_compaction_prioritizes_current_authority_not_superseded_gates(
        self,
    ) -> None:
        skill = (SESSION_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        compact = skill.split("## Compact Instructions\n", 1)[1].split("\n## ", 1)[0]
        priorities = [line for line in compact.splitlines() if line[:1].isdigit()]

        self.assertIn("effective task-scoped approval baseline", priorities[0])
        self.assertIn("source of each approval", priorities[0])
        self.assertIn("not solely in a task-loaded Skill", compact)
        self.assertIn("one current account", compact)
        self.assertIn("historical, not active blockers", compact)
        self.assertIn("verification is not missing authority", compact)
        self.assertIn("approval does not establish that a check passed", compact)

    def test_recovery_does_not_invent_or_revoke_approval_from_memory(self) -> None:
        memory = (SESSION_SKILL_ROOT / "references/memory-boundary.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("trusted task-specific user approvals", memory)
        self.assertIn("outdated project paragraph", memory)
        self.assertIn(
            "cannot grant new permission or restore a superseded gate", memory
        )
        self.assertIn("ask only about that missing boundary", memory)


if __name__ == "__main__":
    unittest.main()
