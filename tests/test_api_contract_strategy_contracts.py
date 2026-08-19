from __future__ import annotations

import unittest
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
API_CONTRACT_ROOT = REPO_ROOT / "skills" / "api-contract-strategy"


class APIContractStrategyRegistrationTests(unittest.TestCase):
    def test_manifest_and_canonical_surface_are_registered(self) -> None:
        with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
            manifest = tomllib.load(handle)["skills"]["api-contract-strategy"]

        self.assertEqual(manifest["category"], "discipline")
        self.assertFalse(manifest["lifecycle_owner"])
        self.assertEqual(manifest["activation_mode"], "native")
        self.assertEqual(manifest["default_role"], "primary")
        self.assertNotIn("implicit_invocation", manifest)
        self.assertFalse(manifest["may_mutate_repo"])
        self.assertFalse(manifest["may_spawn_agent"])

        self.assertTrue((API_CONTRACT_ROOT / "SKILL.md").is_file())
        self.assertTrue(
            (REPO_ROOT / manifest["source"] / "SKILL.md").is_file()
        )


if __name__ == "__main__":
    unittest.main()
