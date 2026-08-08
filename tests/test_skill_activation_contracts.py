from __future__ import annotations

import copy
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import tomllib


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "skill_activation", REPO_ROOT / "scripts" / "skill_activation.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load scripts/skill_activation.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_contract() -> dict[str, object]:
    with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
        return tomllib.load(handle)


class SkillActivationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.activation = load_script()

    def test_current_activation_contract_is_valid(self) -> None:
        self.assertEqual(
            [],
            self.activation.validate_activation_contract(
                load_contract(), REPO_ROOT, check_sources=True
            ),
        )

    def test_projection_table_has_the_approved_capability_mapping(self) -> None:
        contract = load_contract()

        self.assertEqual(
            {
                "baseline": True,
                "conditional": True,
                "controller": False,
                "explicit": False,
                "native": True,
            },
            {
                mode: self.activation.codex_allows_implicit(contract, mode)
                for mode in sorted(self.activation.VALID_ACTIVATION_MODES)
            },
        )

    def test_missing_or_invalid_mode_and_role_are_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["analyze-project"].pop("activation_mode")
        contract["skills"]["design-change"]["activation_mode"] = "sometimes"
        contract["skills"]["plan-change"]["default_role"] = "boss"

        errors = self.activation.validate_activation_contract(
            contract, REPO_ROOT, check_sources=False
        )

        self.assertTrue(any("analyze-project: missing activation_mode" in error for error in errors))
        self.assertTrue(any("design-change: invalid activation_mode" in error for error in errors))
        self.assertTrue(any("plan-change: invalid default_role" in error for error in errors))

    def test_projection_drift_is_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["activation_modes"]["controller"][
            "codex_allow_implicit_invocation"
        ] = True

        errors = self.activation.validate_activation_contract(
            contract, REPO_ROOT, check_sources=False
        )

        self.assertTrue(
            any(
                "activation_modes.controller.codex_allow_implicit_invocation"
                in error
                for error in errors
            )
        )

    def test_authored_legacy_boolean_is_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["analyze-project"]["implicit_invocation"] = True

        errors = self.activation.validate_activation_contract(
            contract, REPO_ROOT, check_sources=False
        )

        self.assertTrue(any("authored implicit_invocation" in error for error in errors))

    def test_unknown_successor_and_successor_cycle_are_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"]["clean-architecture"]["superseded_by"] = "missing"
        contract["skills"]["quality-standards"]["superseded_by"] = "security-logging"
        contract["skills"]["security-logging"]["superseded_by"] = "quality-standards"

        errors = self.activation.validate_activation_contract(
            contract, REPO_ROOT, check_sources=False
        )

        self.assertTrue(any("unknown superseded_by" in error for error in errors))
        self.assertTrue(any("successor graph contains a cycle" in error for error in errors))

    def test_source_policy_and_unsupported_shared_frontmatter_are_rejected(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"] = {"fixture": contract["skills"]["analyze-project"]}
        contract["skills"]["fixture"]["source"] = "src/skills/fixture"
        contract["skills"]["fixture"]["public_id"] = "fixture"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "src" / "skills" / "fixture"
            (skill_dir / "agents").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: fixture
description: Fixture.
disable-model-invocation: true
---
""",
                encoding="utf-8",
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                """interface:
  display_name: Fixture
policy:
  allow_implicit_invocation: true
""",
                encoding="utf-8",
            )

            errors = self.activation.validate_activation_contract(
                contract, root, check_sources=True
            )

        self.assertTrue(any("authored Codex invocation policy" in error for error in errors))
        self.assertTrue(any("unsupported shared frontmatter" in error for error in errors))

    def test_openai_projection_is_deterministic_and_preserves_interface(self) -> None:
        source = """interface:
  display_name: Fixture
  short_description: Keep this text
"""

        projected = self.activation.project_openai_metadata(source, False)

        self.assertIn("display_name: Fixture", projected)
        self.assertIn("short_description: Keep this text", projected)
        self.assertTrue(projected.endswith("policy:\n  allow_implicit_invocation: false\n"))
        self.assertEqual(projected, self.activation.project_openai_metadata(projected, False))

    def test_all_generated_targets_match_activation_projection(self) -> None:
        contract = load_contract()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for target in ("claude", "codex", "root-flat"):
                with self.subTest(target=target):
                    destination = root / target
                    subprocess.run(
                        [
                            sys.executable,
                            str(REPO_ROOT / "scripts" / "flatten-skills.py"),
                            "--target",
                            target,
                            "--dest",
                            str(destination),
                        ],
                        cwd=REPO_ROOT,
                        check=True,
                        text=True,
                        capture_output=True,
                    )
                    subprocess.run(
                        [
                            sys.executable,
                            str(REPO_ROOT / "scripts" / "check-install-surface.py"),
                            "--target",
                            target,
                            "--dest",
                            str(destination),
                        ],
                        cwd=REPO_ROOT,
                        check=True,
                        text=True,
                        capture_output=True,
                    )
                    skills_root = (
                        destination if target == "root-flat" else destination / "skills"
                    )
                    for entry in contract["skills"].values():
                        if target not in entry.get("install", []):
                            continue
                        public_id = entry["public_id"]
                        expected = self.activation.derived_implicit_invocation(
                            contract, entry
                        )
                        metadata = (
                            skills_root / public_id / "agents" / "openai.yaml"
                        ).read_text(encoding="utf-8")
                        self.assertIn(
                            f"allow_implicit_invocation: {str(expected).lower()}",
                            metadata,
                        )
                        skill_text = (
                            skills_root / public_id / "SKILL.md"
                        ).read_text(encoding="utf-8")
                        self.assertNotIn("disable-model-invocation: true", skill_text)


if __name__ == "__main__":
    unittest.main()
