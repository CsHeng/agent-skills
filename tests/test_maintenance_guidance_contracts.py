"""Structural contracts for maintenance guidance and acknowledgement ownership."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
LEVEL_TWO_HEADING = re.compile(r"(?m)^##\s+")


def markdown_links(text: str) -> list[str]:
    """Return Markdown link targets without freezing surrounding prose."""

    return MARKDOWN_LINK.findall(text)


def final_level_two_section(text: str) -> str:
    """Return the final root-level documentation section."""

    sections = LEVEL_TWO_HEADING.split(text)
    if len(sections) < 2:
        raise AssertionError("root README must contain level-two sections")
    return sections[-1]


class MaintenanceGuidanceContractTests(unittest.TestCase):
    def test_organize_docs_retires_legacy_claude_without_compatibility_link(
        self,
    ) -> None:
        skill_path = REPO_ROOT / "skills/organize-docs/SKILL.md"
        skill = skill_path.read_text(encoding="utf-8")

        self.assertIn(
            "When root `CLAUDE.md` is absent, maintain `AGENTS.md` only",
            skill,
        )
        self.assertIn(
            "The final state is a valid `AGENTS.md` and no root `CLAUDE.md` path",
            skill,
        )
        self.assertIn("repository-wide legacy-file cleanup", skill)
        self.assertNotIn("retain `CLAUDE.md`", skill)
        self.assertNotIn("`CLAUDE.md` remains a symlink", skill)

        migration_links = [
            link
            for link in markdown_links(skill)
            if Path(link).name == "legacy-claude-migration.md"
        ]
        self.assertEqual(1, len(migration_links))

        migration = (skill_path.parent / migration_links[0]).read_text(
            encoding="utf-8"
        )
        self.assertIn("unlink only", migration)
        self.assertIn(
            "never edit, write through, or replace the link target",
            migration,
        )
        self.assertIn(
            "Reading or migrating the target is not a prerequisite for deleting the link",
            migration,
        )
        self.assertIn("rename `CLAUDE.md` to `AGENTS.md`", migration)
        self.assertIn("merge only still-valid unique guidance", migration)
        self.assertIn(
            "Never overwrite existing `AGENTS.md` content or discard "
            "still-valid `CLAUDE.md` guidance",
            migration,
        )
        self.assertIn(
            "Removing a symlink does not create `AGENTS.md`",
            migration,
        )
        self.assertIn(
            "does not exist as a file, symlink, or dangling symlink",
            migration,
        )
        self.assertIn(
            "directory, device, socket, or another unsafe type",
            migration,
        )
        self.assertNotIn("relative symlink `CLAUDE.md -> AGENTS.md`", migration)

    def test_skill_miner_scopes_project_context_to_readme_and_agents(self) -> None:
        skill = (REPO_ROOT / "skills/skill-miner/SKILL.md").read_text(
            encoding="utf-8"
        )

        project_context_lines = [
            line for line in skill.splitlines() if "Project context docs:" in line
        ]
        self.assertEqual(1, len(project_context_lines))
        self.assertIn("`README.md`", project_context_lines[0])
        self.assertIn("`AGENTS.md`", project_context_lines[0])
        self.assertNotIn("CLAUDE.md", skill)

    def test_organize_docs_decision_lifecycle_reference_resolves(self) -> None:
        skill_path = REPO_ROOT / "skills/organize-docs/SKILL.md"
        links = markdown_links(skill_path.read_text(encoding="utf-8"))
        lifecycle_links = [
            link for link in links if Path(link).name == "decision-record-lifecycle.md"
        ]

        self.assertEqual(1, len(lifecycle_links))
        self.assertTrue((skill_path.parent / lifecycle_links[0]).is_file())

    def test_root_readme_owns_inspiration_links(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        acknowledgement_links = {
            link
            for link in markdown_links(final_level_two_section(readme))
            if link.startswith(("https://", "http://"))
        }
        self.assertTrue(acknowledgement_links)

        stable_log = (
            REPO_ROOT / "docs/changelog/design-decisions.md"
        ).read_text(encoding="utf-8")
        skill_payload = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for root in (REPO_ROOT / "skills",)
            for path in root.rglob("*")
            if path.is_file()
        )

        for link in acknowledgement_links:
            with self.subTest(link=link):
                self.assertNotIn(link, stable_log)
                self.assertNotIn(link, skill_payload)


if __name__ == "__main__":
    unittest.main()
