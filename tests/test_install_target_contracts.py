"""Contracts for the sole root-flat materialization target."""

from __future__ import annotations

import json
import tempfile
import tomllib
import unittest
from pathlib import Path

from scripts.skill_distribution import (
    DistributionError,
    build_validated_surface,
    replace_directory,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class InstallTargetContractTests(unittest.TestCase):
    def test_live_symlinks_are_the_recommended_management_mode(self) -> None:
        with (REPO_ROOT / "contracts" / "install-targets.toml").open("rb") as handle:
            distribution = tomllib.load(handle)["distribution"]
        self.assertEqual("live-symlink", distribution["recommended_management"])
        self.assertEqual("per-skill", distribution["recommended_symlink_layout"])
        self.assertEqual("~/.agents/skills", distribution["recommended_user_root"])
        self.assertEqual("local-git-checkout", distribution["recommended_source"])
        self.assertEqual("git-pull", distribution["recommended_update"])
        self.assertEqual("compatible-optional", distribution["plugin_policy"])
        self.assertEqual(
            "compatible-not-recommended", distribution["long_tail_policy"]
        )
        self.assertEqual(
            "one-active-discovery-path-per-tool-and-public-id",
            distribution["duplicate_invariant"],
        )

    def test_root_flat_is_the_only_materialization_target(self) -> None:
        with (REPO_ROOT / "contracts" / "install-targets.toml").open("rb") as handle:
            contract = tomllib.load(handle)
        self.assertEqual("root-flat", contract["distribution"]["materialization_target"])
        self.assertEqual({"root-flat"}, set(contract["targets"]))
        self.assertEqual("skills", contract["targets"]["root-flat"]["dest"])
        generator = (REPO_ROOT / "scripts" / "flatten-skills.py").read_text(encoding="utf-8")
        self.assertNotIn("claude", generator)
        self.assertNotIn("codex", generator)

    def test_both_provider_manifests_share_the_root_flat_package(self) -> None:
        expected_repository = "https://github.com/CsHeng/agent-skills"
        for manifest_path in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            manifest = json.loads((REPO_ROOT / manifest_path).read_text(encoding="utf-8"))
            self.assertEqual(expected_repository, manifest["homepage"])
            self.assertEqual(expected_repository, manifest["repository"])
        self.assertTrue((REPO_ROOT / "skills").is_dir())

    def test_replacement_failure_preserves_preceding_tree_byte_for_byte(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "skills"
            staged = root / "staged"
            destination.mkdir()
            staged.mkdir()
            (destination / "before.txt").write_bytes(b"before\x00tree")
            (staged / "after.txt").write_bytes(b"after\x00tree")
            before = {path.name: path.read_bytes() for path in destination.iterdir()}

            def fail_promote(source: Path, target: Path) -> None:
                raise OSError(f"injected promotion failure: {source} -> {target}")

            with self.assertRaises(OSError):
                replace_directory(staged, destination, fail_promote)
            after = {path.name: path.read_bytes() for path in destination.iterdir()}
            self.assertEqual(before, after)

    def test_validation_failure_never_touches_preceding_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "skills"
            destination.mkdir()
            (destination / "before.txt").write_bytes(b"preceding tree")
            before = (destination / "before.txt").read_bytes()

            def invalid_renderer(repo_root: Path, staged: Path) -> None:
                del repo_root
                staged.mkdir()
                (staged / "partial.txt").write_text("partial", encoding="utf-8")
                raise DistributionError("injected validation failure")

            with self.assertRaises(DistributionError):
                build_validated_surface(root, root, invalid_renderer)
            self.assertEqual(before, (destination / "before.txt").read_bytes())
            self.assertEqual(["before.txt"], [path.name for path in destination.iterdir()])


if __name__ == "__main__":
    unittest.main()
