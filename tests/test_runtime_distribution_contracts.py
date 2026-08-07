from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import ModuleType

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = REPO_ROOT / "src/runtime/harness"
RUNTIME_OWNERS = {
    "close-change",
    "design-change",
    "implement-change",
    "plan-change",
    "review-change",
    "sync-truth",
}


def load_contract() -> dict[str, object]:
    with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
        return tomllib.load(handle)


def load_generator() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "flatten_skills_runtime_test", REPO_ROOT / "scripts/flatten-skills.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load scripts/flatten-skills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def production_runtime_files() -> dict[str, Path]:
    return {
        path.relative_to(RUNTIME_ROOT).as_posix(): path
        for path in RUNTIME_ROOT.rglob("*")
        if path.is_file()
        and path.relative_to(RUNTIME_ROOT).parts[0] not in {"agents", "smoke-test"}
        and path.name != "SKILL.md"
    }


class RuntimeDistributionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.generator = load_generator()

    def test_runtime_source_is_not_a_discoverable_skill(self) -> None:
        self.assertTrue(RUNTIME_ROOT.is_dir())
        self.assertFalse((RUNTIME_ROOT / "SKILL.md").exists())
        self.assertFalse((REPO_ROOT / "src/skills/_internal/_harness-libs").exists())

        contract = load_contract()
        public_ids = {
            entry["public_id"] for entry in contract["skills"].values()  # type: ignore[union-attr]
        }
        self.assertNotIn("_harness-libs", public_ids)

    def test_runtime_owners_and_semantic_profile_are_explicit(self) -> None:
        contract = load_contract()
        skills = contract["skills"]  # type: ignore[assignment]
        runtime_owners = {
            entry["public_id"]
            for entry in skills.values()
            if entry.get("runtime_bundle") == "harness"
        }
        self.assertEqual(RUNTIME_OWNERS, runtime_owners)

        semantic_install = contract["semantic_install"]
        self.assertEqual("consumer", semantic_install["dependency_resolution"])
        self.assertTrue(
            semantic_install["selective_install_requires_transitive_closure"]
        )
        self.assertEqual("sovereign-harness", semantic_install["complete_profile"])
        self.assertEqual(
            "all-public",
            contract["profiles"]["sovereign-harness"]["selection"],
        )

        by_public_id = {entry["public_id"]: entry for entry in skills.values()}
        self.assertEqual(
            ["review-change"], by_public_id["design-change"]["semantic_requires"]
        )
        self.assertEqual(
            ["review-change"], by_public_id["plan-change"]["semantic_requires"]
        )
        self.assertEqual(
            ["review-change", "sync-truth", "close-change"],
            by_public_id["implement-change"]["semantic_requires"],
        )
        self.assertEqual(
            ["review-design", "review-plan", "review-implementation"],
            by_public_id["review-change"]["semantic_requires"],
        )

    def test_generated_codex_surface_contains_exact_runtime_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "codex"
            result = subprocess.run(
                [
                    "python3",
                    "scripts/flatten-skills.py",
                    "--target",
                    "codex",
                    "--dest",
                    str(destination),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)

            expected_runtime = production_runtime_files()
            self.assertTrue(expected_runtime)
            entry_commands = {
                "close-change": ("close-runner.sh", "entry-phase", "close"),
                "design-change": ("design-runner.sh", "entry-phase", "clarify"),
                "implement-change": (
                    "execute-runner.sh",
                    "entry-phase",
                    "implement-serial",
                ),
                "plan-change": ("plan-runner.sh", "entry-phase", "plan"),
                "review-change": ("design-runner.sh", "entry-phase", "clarify"),
                "sync-truth": (
                    "truth-sync-runner.sh",
                    "entry-phase",
                    "truth-sync",
                ),
            }
            for public_id in RUNTIME_OWNERS:
                with self.subTest(skill=public_id):
                    bundle = destination / "skills" / public_id / "scripts/harness"
                    actual_runtime = {
                        path.relative_to(bundle).as_posix(): path
                        for path in bundle.rglob("*")
                        if path.is_file()
                    }
                    self.assertEqual(set(expected_runtime), set(actual_runtime))
                    for relative_path, source_file in expected_runtime.items():
                        self.assertEqual(
                            source_file.read_bytes(),
                            actual_runtime[relative_path].read_bytes(),
                        )
                    runner_name, operation, expected_output = entry_commands[public_id]
                    invocation = subprocess.run(
                        ["bash", str(bundle / runner_name), operation],
                        cwd=temp_dir,
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    self.assertEqual(0, invocation.returncode, invocation.stderr)
                    self.assertEqual(expected_output, invocation.stdout.strip())

            self.assertFalse((destination / "skills/_harness-libs").exists())

    def test_generated_index_exposes_direct_and_transitive_requirements(self) -> None:
        index = json.loads(
            (REPO_ROOT / "skills.index.json").read_text(encoding="utf-8")
        )
        by_public_id = {entry["public_id"]: entry for entry in index["skills"]}
        self.assertNotIn("_harness-libs", by_public_id)
        self.assertEqual(
            ["review-change", "sync-truth", "close-change"],
            by_public_id["implement-change"]["semantic_requires"],
        )
        self.assertEqual(
            [
                "close-change",
                "review-change",
                "review-design",
                "review-implementation",
                "review-plan",
                "sync-truth",
            ],
            by_public_id["implement-change"]["semantic_transitive_requires"],
        )

        profile = index["profiles"]["sovereign-harness"]
        self.assertEqual("all-public", profile["selection"])
        self.assertEqual(sorted(by_public_id), profile["skills"])
        self.assertTrue(profile["semantic_closure_complete"])

    def test_generator_rejects_nonportable_root_assumptions(self) -> None:
        fixtures = {
            "retired.md": "Use ../_harness-libs/plan-runner.sh\n",
            "provider.md": 'RUNNER="$CLAUDE_PLUGIN_ROOT/runner.sh"\n',
            "ambient.md": 'RUNNER="$SKILL_ROOT/runner.sh"\n',
        }
        for file_name, content in fixtures.items():
            with self.subTest(file=file_name), tempfile.TemporaryDirectory() as temp_dir:
                skill_root = Path(temp_dir)
                (skill_root / file_name).write_text(content, encoding="utf-8")
                with self.assertRaises(SystemExit):
                    self.generator.assert_portable_content("fixture", skill_root)

    def test_generator_accepts_explicit_skill_root_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_root = Path(temp_dir)
            (skill_root / "SKILL.md").write_text(
                'SKILL_ROOT="/absolute/path/to/fixture"\n'
                'RUNNER="$SKILL_ROOT/scripts/runner.sh"\n',
                encoding="utf-8",
            )

            self.generator.assert_portable_content("fixture", skill_root)


if __name__ == "__main__":
    unittest.main()
