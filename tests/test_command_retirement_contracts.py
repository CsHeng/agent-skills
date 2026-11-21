from __future__ import annotations

import os
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def load_contract() -> dict[str, object]:
    with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
        return tomllib.load(handle)


class CommandRetirementContractTests(unittest.TestCase):
    def test_retired_commands_are_not_active_product_entrypoints(self) -> None:
        contract = load_contract()
        self.assertFalse(any((REPO_ROOT / "commands").glob("*.md")))
        self.assertNotIn("check-secrets", contract["skills"])
        self.assertNotIn("command_retirement", contract)

    def test_provider_adapters_remain_active(self) -> None:
        retained_paths = (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".codex-plugin/plugin.json",
            ".codex-marketplace/.agents/plugins/marketplace.json",
            ".codex-marketplace/plugins/coding",
            "install.sh",
            "install-codex.sh",
            "hooks/post-edit-check.sh",
        )
        if os.environ.get("STANDALONE_CHECK_ACTIVE") == "1":
            retained_paths = tuple(
                path
                for path in retained_paths
                if path != ".codex-marketplace/plugins/coding"
            )
        for relative_path in retained_paths:
            with self.subTest(path=relative_path):
                self.assertTrue((REPO_ROOT / relative_path).exists())


if __name__ == "__main__":
    unittest.main()
