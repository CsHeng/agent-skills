from __future__ import annotations

import copy
import importlib.util
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
                "composition": False,
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
        contract["activation_modes"]["composition"][
            "codex_allow_implicit_invocation"
        ] = True

        errors = self.activation.validate_activation_contract(
            contract, REPO_ROOT, check_sources=False
        )

        self.assertTrue(
            any(
                "activation_modes.composition.codex_allow_implicit_invocation"
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

    def test_canonical_metadata_projection_and_frontmatter_are_checked(self) -> None:
        contract = copy.deepcopy(load_contract())
        contract["skills"] = {"fixture": contract["skills"]["analyze-project"]}
        contract["skills"]["fixture"]["activation_mode"] = "composition"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "skills" / "fixture"
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

        self.assertTrue(any("Codex invocation projection is stale" in error for error in errors))
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

    def test_canonical_tree_matches_activation_projection(self) -> None:
        contract = load_contract()
        for skill_id, entry in contract["skills"].items():
            with self.subTest(skill=skill_id):
                expected = self.activation.derived_implicit_invocation(contract, entry)
                metadata = (
                    REPO_ROOT / "skills" / skill_id / "agents" / "openai.yaml"
                ).read_text(encoding="utf-8")
                self.assertIn(
                    f"allow_implicit_invocation: {str(expected).lower()}", metadata
                )


if __name__ == "__main__":
    unittest.main()
