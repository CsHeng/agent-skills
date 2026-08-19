"""Contracts for nested authoring, root-flat projection, and skill-local runtimes."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNTIME = REPO_ROOT / "src" / "runtime" / "harness"
RUNTIME_OWNERS = {
    "close-change",
    "design-change",
    "implement-change",
    "plan-change",
    "review-change",
    "sync-truth",
}
RETIRED_IDS = {"clean-architecture", "quality-standards", "security-logging"}


class RuntimeDistributionContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
            cls.contract = tomllib.load(handle)
        cls.skills = cls.contract["skills"]

    def test_authored_and_generated_trees_have_exact_39_skill_mapping(self) -> None:
        generated = {path.name for path in (REPO_ROOT / "skills").glob("*/")}
        self.assertEqual(39, len(self.skills))
        self.assertEqual(set(self.skills), generated)
        self.assertFalse(RETIRED_IDS & generated)
        source_map = json.loads(
            (REPO_ROOT / "skills" / ".source-map.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {skill_id: entry["source"] for skill_id, entry in self.skills.items()},
            source_map,
        )
        self.assertEqual(len(source_map), len(set(source_map.values())))
        actual_authored_sources = {
            path.parent.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "src" / "skills").rglob("SKILL.md")
        }
        self.assertEqual(set(source_map.values()), actual_authored_sources)
        for skill_id, source in source_map.items():
            with self.subTest(skill=skill_id):
                source_dir = REPO_ROOT / source
                self.assertTrue((source_dir / "SKILL.md").is_file())
                self.assertTrue(source_dir.is_relative_to(REPO_ROOT / "src" / "skills"))
                metadata = source_dir / "agents" / "openai.yaml"
                if metadata.is_file():
                    self.assertNotIn(
                        "allow_implicit_invocation",
                        metadata.read_text(encoding="utf-8"),
                    )

    def test_source_runtime_is_single_authored_python_package(self) -> None:
        self.assertTrue((SOURCE_RUNTIME / "cli.py").is_file())
        self.assertFalse((SOURCE_RUNTIME / "SKILL.md").exists())
        self.assertFalse((REPO_ROOT / "runtime").exists())
        self.assertFalse(any(SOURCE_RUNTIME.glob("*.sh")))
        result = subprocess.run(
            [sys.executable, str(SOURCE_RUNTIME / "cli.py"), "--help"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_exact_six_generated_runtime_bundles_match_manifest(self) -> None:
        owners = {
            skill_id
            for skill_id, entry in self.skills.items()
            if entry.get("runtime_bundle") == "harness"
        }
        self.assertEqual(RUNTIME_OWNERS, owners)
        with (REPO_ROOT / "contracts" / "runtime-bundles.toml").open("rb") as handle:
            bundle = tomllib.load(handle)["bundles"]["harness"]
        expected = set(bundle["files"])
        for skill_id in self.skills:
            bundle_dir = REPO_ROOT / "skills" / skill_id / bundle["destination"]
            if skill_id not in owners:
                self.assertFalse(bundle_dir.exists(), skill_id)
                continue
            actual = {
                path.relative_to(bundle_dir).as_posix()
                for path in bundle_dir.rglob("*")
                if path.is_file()
            }
            self.assertEqual(expected, actual, skill_id)
            for relative in expected:
                source = REPO_ROOT / bundle["source"] / relative
                generated = bundle_dir / relative
                self.assertEqual(
                    source.read_bytes(), generated.read_bytes(), f"{skill_id}/{relative}"
                )

    def test_each_runtime_owner_is_standalone_after_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            unrelated = Path(temporary)
            for skill_id in sorted(RUNTIME_OWNERS):
                copied = unrelated / skill_id
                subprocess.run(
                    ["cp", "-R", str(REPO_ROOT / "skills" / skill_id), str(copied)],
                    check=True,
                )
                result = subprocess.run(
                    [sys.executable, str(copied / "scripts" / "harness" / "cli.py"), "--help"],
                    cwd=unrelated,
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, result.returncode, f"{skill_id}: {result.stderr}")

    def test_lifecycle_skills_resolve_only_skill_local_cli(self) -> None:
        for skill_id in RUNTIME_OWNERS:
            text = (REPO_ROOT / "skills" / skill_id / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("$SKILL_ROOT/scripts/harness/cli.py", text, skill_id)
            self.assertNotIn("../../runtime/harness", text, skill_id)

    def test_retired_ids_and_shell_runtime_remain_absent(self) -> None:
        self.assertFalse(RETIRED_IDS & set(self.skills))
        self.assertFalse(any(SOURCE_RUNTIME.rglob("*.sh")))
        for retired_id in RETIRED_IDS:
            self.assertFalse((REPO_ROOT / "skills" / retired_id).exists())

    def test_index_keeps_semantic_identity(self) -> None:
        index = json.loads((REPO_ROOT / "skills.index.json").read_text(encoding="utf-8"))
        by_id = {entry["id"]: entry for entry in index["skills"]}
        self.assertEqual(39, index["canonical_skill_count"])
        self.assertEqual(set(self.skills), set(by_id))
        self.assertEqual(
            ["review-change", "sync-truth", "close-change"],
            by_id["implement-change"]["semantic_requires"],
        )

    def test_source_map_digest_is_deterministic(self) -> None:
        source_map = REPO_ROOT / "skills" / ".source-map.json"
        first = hashlib.sha256(source_map.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, "scripts/flatten-skills.py", "--target", "root-flat", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertEqual(first, hashlib.sha256(source_map.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
