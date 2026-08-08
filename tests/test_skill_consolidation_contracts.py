from __future__ import annotations

import unittest
from pathlib import Path

import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "src" / "skills"


class SkillConsolidationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
            cls.contract = tomllib.load(handle)
        routing_path = (
            SKILL_ROOT
            / "session"
            / "use-coding-skills"
            / "references"
            / "routing.toml"
        )
        with routing_path.open("rb") as handle:
            cls.routing = tomllib.load(handle)

    def test_compatibility_helpers_are_explicit_non_owners(self) -> None:
        expected = {
            "clean-architecture": "architecture-patterns",
            "quality-standards": "development-standards",
            "security-logging": "logging-standards",
        }
        case_owners = {case["owner"] for case in self.routing["trigger_cases"]}

        for public_id, successor in expected.items():
            with self.subTest(skill=public_id):
                entry = self.contract["skills"][public_id]
                self.assertEqual(entry["activation_mode"], "explicit")
                self.assertEqual(entry["default_role"], "helper")
                self.assertEqual(entry["superseded_by"], successor)
                self.assertNotIn(public_id, case_owners)
                body = (REPO_ROOT / entry["source"] / "SKILL.md").read_text(
                    encoding="utf-8"
                )
                self.assertLessEqual(len(body.splitlines()), 32)
                self.assertIn(successor, body)
                self.assertIn("explicitly", body.lower())
                self.assertNotIn("## IO Semantics", body)
                self.assertNotIn("## Checklist", body)

    def test_clean_boundary_guidance_has_one_durable_owner(self) -> None:
        reference = (
            SKILL_ROOT
            / "disciplines"
            / "architecture-patterns"
            / "references"
            / "clean-boundaries.md"
        )
        text = reference.read_text(encoding="utf-8")
        architecture_skill = (
            SKILL_ROOT / "disciplines" / "architecture-patterns" / "SKILL.md"
        ).read_text(encoding="utf-8")

        for phrase in (
            "dependency direction",
            "interface placement",
            "handlers",
            "services",
            "repositories",
            "cross-boundary tests",
        ):
            self.assertIn(phrase, text.lower())
        self.assertIn("references/clean-boundaries.md", architecture_skill)
        active_text = architecture_skill + "\n" + text
        self.assertNotIn("python-services-dev", active_text)
        self.assertNotIn("go-services-dev", active_text)

    def test_quality_gates_are_repository_owned_not_universal_thresholds(self) -> None:
        standards = (
            SKILL_ROOT / "policies" / "development-standards" / "SKILL.md"
        ).read_text(encoding="utf-8")
        helper_root = SKILL_ROOT / "policies" / "quality-standards"
        helper = (helper_root / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("repository-owned quality gates", standards.lower())
        self.assertIn("testing-strategy", standards)
        self.assertIn("language", standards.lower())
        combined = standards + "\n" + helper
        for stale_rule in (
            "maintainability index: 70",
            "max-complexity to 10",
            "complexity ≤ 5",
            "coverage thresholds",
        ):
            self.assertNotIn(stale_rule, combined.lower())
        self.assertFalse((helper_root / "references" / "examples-python.md").exists())
        self.assertFalse((helper_root / "references" / "linter-configs.md").exists())

    def test_security_audit_logging_and_exploit_controls_have_distinct_owners(self) -> None:
        logging_reference = (
            SKILL_ROOT
            / "policies"
            / "logging-standards"
            / "references"
            / "security-and-audit-logging.md"
        ).read_text(encoding="utf-8")
        security = (
            SKILL_ROOT / "policies" / "security-guardrails" / "SKILL.md"
        ).read_text(encoding="utf-8")
        helper_root = SKILL_ROOT / "policies" / "security-logging"

        for phrase in (
            "event selection",
            "redaction",
            "correlation",
            "retention",
            "access",
            "tamper evidence",
        ):
            self.assertIn(phrase, logging_reference.lower())
        for phrase in ("input validation", "sql injection", "file upload", "cors", "tls"):
            self.assertIn(phrase, security.lower())
        self.assertFalse((helper_root / "references" / "examples-python.md").exists())
        self.assertFalse((helper_root / "references" / "secret-scanner.md").exists())


if __name__ == "__main__":
    unittest.main()
