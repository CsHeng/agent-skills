"""Installation boundaries for the directly authored Skill collection."""

from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class InstallTargetContractTests(unittest.TestCase):
    def test_installation_uses_independent_copies_and_explicit_updates(self) -> None:
        with (REPO_ROOT / "contracts" / "install-targets.toml").open("rb") as handle:
            installation = tomllib.load(handle)["installation"]
        self.assertEqual("skills", installation["source"])
        self.assertEqual("npx skills@latest", installation["recommended_manager"])
        self.assertEqual("~/.agents/skills", installation["recommended_user_root"])
        self.assertEqual("independent-copy", installation["content_boundary"])
        self.assertEqual("explicit-install-or-update", installation["update_policy"])
        self.assertEqual(
            "one-active-discovery-path-per-tool-and-public-id",
            installation["duplicate_invariant"],
        )

    def test_both_provider_manifests_share_the_authored_collection(self) -> None:
        expected_repository = "https://github.com/CsHeng/agent-skills"
        for manifest_path in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
            manifest = json.loads((REPO_ROOT / manifest_path).read_text(encoding="utf-8"))
            self.assertEqual(expected_repository, manifest["homepage"])
            self.assertEqual(expected_repository, manifest["repository"])
        self.assertTrue((REPO_ROOT / "skills").is_dir())


if __name__ == "__main__":
    unittest.main()
