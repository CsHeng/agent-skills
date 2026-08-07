"""Contract tests for generated install-surface destination resolution."""

from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path
from types import ModuleType

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_script(module_name: str, script_name: str) -> ModuleType:
    """Load a repository script as a testable module."""
    spec = importlib.util.spec_from_file_location(
        module_name, REPO_ROOT / "scripts" / script_name
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load scripts/{script_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FLATTEN_SKILLS = load_script("flatten_skills", "flatten-skills.py")
CHECK_INSTALL_SURFACE = load_script("check_install_surface", "check-install-surface.py")


class InstallTargetContractTests(unittest.TestCase):
    """Keep generator and validator defaults aligned with install-target contracts."""

    def test_external_default_destinations_resolve_under_dist(self) -> None:
        expected_destinations = {
            "claude": REPO_ROOT / ".dist/claude",
            "codex": REPO_ROOT / ".dist/codex",
        }

        for target_name, expected_destination in expected_destinations.items():
            with self.subTest(target=target_name):
                resolved_destination = expected_destination.resolve()
                self.assertEqual(
                    resolved_destination,
                    FLATTEN_SKILLS.target_dest(target_name, None),
                )
                self.assertEqual(
                    resolved_destination,
                    CHECK_INSTALL_SURFACE.target_dest(target_name, None),
                )

    def test_hybrid_distribution_contract_keeps_provider_plugins_and_names(self) -> None:
        with (REPO_ROOT / "contracts/install-targets.toml").open("rb") as handle:
            contract = tomllib.load(handle)

        distribution = contract["distribution"]
        self.assertEqual(["claude", "codex"], distribution["provider_plugin_targets"])
        self.assertEqual("root-flat", distribution["shared_payload_target"])
        self.assertEqual("npx skills@latest", distribution["long_tail_cli"])
        self.assertEqual("advisory", distribution["long_tail_policy"])
        self.assertEqual("consumer", distribution["long_tail_owner"])
        self.assertFalse(distribution["enforce_destinations"])
        self.assertFalse(distribution["detect_duplicates"])
        self.assertFalse(distribution["coexistence_guaranteed"])
        self.assertEqual("", distribution["public_name_prefix"])
        self.assertNotIn("long_tail_required_flags", distribution)
        self.assertNotIn("long_tail_excluded_agents", distribution)
        self.assertFalse(
            contract["targets"]["claude"]["include_internal_runtime_support"]
        )
        self.assertFalse(
            contract["targets"]["codex"]["include_internal_runtime_support"]
        )
        self.assertFalse(
            contract["targets"]["root-flat"]["include_internal_runtime_support"]
        )

    def test_readme_keeps_external_installation_advisory(self) -> None:
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("npx skills@latest add CsHeng/agent-skills", readme)
        self.assertIn("does not restrict selected agents", readme)
        self.assertIn("does not inspect duplicate exposure", readme)
        self.assertIn("promise that independently installed copies coexist", readme)
        self.assertIn("https://github.com/obra/superpowers", readme)
        self.assertIn("contracts and lifecycle rules", readme.lower())
        self.assertNotIn("~/.agents/skills/coding", readme)

    def test_provider_manifests_use_current_repository(self) -> None:
        expected_repository = "https://github.com/CsHeng/agent-skills"
        for manifest_path in (
            ".claude-plugin/plugin.json",
            ".codex-plugin/plugin.json",
        ):
            with self.subTest(manifest=manifest_path):
                manifest = json.loads(
                    (REPO_ROOT / manifest_path).read_text(encoding="utf-8")
                )
                self.assertEqual(expected_repository, manifest["homepage"])
                self.assertEqual(expected_repository, manifest["repository"])


if __name__ == "__main__":
    unittest.main()
