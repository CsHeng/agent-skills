"""Static distribution boundaries for the semantic-only Skill collection."""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from scripts.skill_portability import validate_portability

REPO_ROOT = Path(__file__).resolve().parents[1]
REMOVED_SURFACES = (
    Path(".pi"),
    Path("integrations") / "pi",
    Path("src") / "runtime" / "harness",
    Path("scripts") / ("generate-" + "pi-contracts.py"),
    Path("contracts") / ("runtime-" + "bundles.toml"),
)


class RuntimeDistributionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            cls.skills = tomllib.load(handle)["skills"]

    def test_authored_tree_matches_public_inventory(self) -> None:
        authored = {path.parent.name for path in (REPO_ROOT / "skills").glob("*/SKILL.md")}
        self.assertEqual(set(self.skills), authored)

    def test_checker_rejects_nested_skill_entrypoints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for directory in ("scripts", "contracts", "skills"):
                shutil.copytree(REPO_ROOT / directory, root / directory)
            shutil.copy2(REPO_ROOT / "pyproject.toml", root / "pyproject.toml")

            def check() -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    [sys.executable, "scripts/check-contracts.py"],
                    cwd=root,
                    env={"PYTHONDONTWRITEBYTECODE": "1"},
                    capture_output=True,
                    text=True,
                    check=False,
                )

            clean = check()
            self.assertEqual(0, clean.returncode, clean.stderr)
            nested = root / "skills/uncontracted/nested/SKILL.md"
            nested.parent.mkdir(parents=True)
            nested.write_text(
                "---\nname: nested\ndescription: Fixture.\n---\n", encoding="utf-8"
            )

            result = check()

        self.assertEqual(1, result.returncode, result.stderr)
        self.assertIn("skills/uncontracted/nested/SKILL.md", result.stderr)

    def test_executable_workflow_surfaces_are_absent(self) -> None:
        for relative in REMOVED_SURFACES:
            with self.subTest(path=relative):
                self.assertFalse((REPO_ROOT / relative).exists())
        self.assertFalse(any((REPO_ROOT / "skills").glob("*/scripts/harness")))

    def test_manifest_has_no_runtime_ownership_fields(self) -> None:
        for skill_id, entry in self.skills.items():
            with self.subTest(skill=skill_id):
                self.assertNotIn("runtime_bundle", entry)
                self.assertNotIn("runtime_contract", entry)

    def test_static_checker_rejects_executable_and_package_coupled_fixtures(self) -> None:
        spec = importlib.util.spec_from_file_location(
            "check_contracts_semantic_only", REPO_ROOT / "scripts/check-contracts.py"
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load contract checker")
        checker = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(checker)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "coding-harness-development"\n', encoding="utf-8"
            )
            (root / "contracts").mkdir()
            (root / "contracts/skills.toml").write_text(
                '[skills.example]\ncategory = "workflow"\n', encoding="utf-8"
            )
            script = root / "skills/example/scripts/runtime.py"
            script.parent.mkdir(parents=True)
            script.write_text("pass\n", encoding="utf-8")
            errors = checker.validate_semantic_only_surface(root)
        self.assertTrue(any("executable support" in error for error in errors))
        self.assertTrue(any("package identity" in error for error in errors))


class SkillPortabilityTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.surface = Path(temporary.name) / "skills"
        self.skill = self.surface / "example"
        self.skill.mkdir(parents=True)

    def write(self, relative: str, body: str) -> Path:
        path = self.skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def test_relative_references_and_scripts_remain_inside_the_installed_skill(self) -> None:
        self.write("SKILL.md", "[guide](references/guide.md)\n[tool](scripts/check.py)\n")
        self.write("references/guide.md", "[skill](../SKILL.md)\n")
        self.write("scripts/check.py", "print('portable')\n")

        self.assertEqual([], validate_portability(self.surface))

    def test_missing_reference_is_rejected(self) -> None:
        self.write("SKILL.md", "[missing](references/missing.md)\n")

        errors = validate_portability(self.surface)

        self.assertTrue(any("references/missing.md" in error for error in errors))

    def test_references_cannot_depend_on_another_skill_directory(self) -> None:
        other = self.surface / "other"
        other.mkdir()
        (other / "SKILL.md").write_text("# Other\n", encoding="utf-8")
        self.write("SKILL.md", "[other](../other/SKILL.md)\n")

        errors = validate_portability(self.surface)

        self.assertTrue(any("../other/SKILL.md" in error for error in errors))

    def test_external_links_anchors_and_fenced_examples_are_not_resources(self) -> None:
        self.write(
            "SKILL.md",
            "[web](https://example.com/guide)\n[section](#usage)\n"
            "```markdown\n[example](nonexistent.md)\n```\n",
        )

        self.assertEqual([], validate_portability(self.surface))

    def test_provider_root_dependencies_are_rejected(self) -> None:
        for token in ("$PLUGIN_ROOT", "${PLUGIN_ROOT}", "$CLAUDE_PLUGIN_ROOT", "${CLAUDE_PLUGIN_ROOT}"):
            with self.subTest(token=token):
                self.write("scripts/check.sh", f'cat "{token}/shared.json"\n')

                errors = validate_portability(self.surface)

                self.assertTrue(any("assumes provider root" in error for error in errors))

    def test_symlinks_cannot_escape_the_installed_skill(self) -> None:
        self.write("SKILL.md", "# Example\n")
        outside = self.surface.parent / "outside.md"
        outside.write_text("outside\n", encoding="utf-8")
        (self.skill / "outside.md").symlink_to(outside)

        self.assertTrue(validate_portability(self.surface))


if __name__ == "__main__":
    unittest.main()
