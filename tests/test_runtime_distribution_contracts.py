"""Static distribution boundaries for the semantic-only Skill collection."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


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

    def test_authored_and_generated_trees_have_exact_40_skill_mapping(self) -> None:
        generated = {path.name for path in (REPO_ROOT / "skills").glob("*/")}
        self.assertEqual(40, len(self.skills))
        self.assertEqual(set(self.skills), generated)
        source_map = json.loads(
            (REPO_ROOT / "skills/.source-map.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {skill_id: entry["source"] for skill_id, entry in self.skills.items()},
            source_map,
        )

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

    def test_index_keeps_semantic_identity(self) -> None:
        index = json.loads((REPO_ROOT / "skills.index.json").read_text(encoding="utf-8"))
        by_id = {entry["id"]: entry for entry in index["skills"]}
        self.assertEqual(40, index["canonical_skill_count"])
        self.assertEqual(set(self.skills), set(by_id))
        self.assertEqual(["review-change"], by_id["implement-change"]["semantic_requires"])

    def test_source_map_digest_is_deterministic(self) -> None:
        source_map = REPO_ROOT / "skills/.source-map.json"
        first = hashlib.sha256(source_map.read_bytes()).hexdigest()
        result = subprocess.run(
            [sys.executable, "scripts/flatten-skills.py", "--target", "root-flat", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr.decode())
        self.assertEqual(first, hashlib.sha256(source_map.read_bytes()).hexdigest())

    def test_static_checker_rejects_executable_and_provider_coupled_fixtures(self) -> None:
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
            script = root / "src/skills/workflows/example/scripts/runtime.py"
            script.parent.mkdir(parents=True)
            script.write_text("pass\n", encoding="utf-8")
            skill = root / "src/skills/example/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text("active host harness\n", encoding="utf-8")
            errors = checker.validate_semantic_only_surface(root)
        self.assertTrue(any("executable support" in error for error in errors))
        self.assertTrue(any("provider-coupled" in error for error in errors))
        self.assertTrue(any("package identity" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
