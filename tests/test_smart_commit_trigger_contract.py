from __future__ import annotations

import unittest
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]


class SmartCommitTriggerContractTest(unittest.TestCase):
    def test_contract_allows_intent_gated_model_selection(self) -> None:
        with (REPO_ROOT / "contracts" / "skills.toml").open("rb") as handle:
            contract = tomllib.load(handle)["skills"]["smart-commit"]

        self.assertEqual(contract["category"], "tool")
        self.assertEqual(contract["activation_mode"], "native")
        self.assertEqual(contract["default_role"], "primary")
        self.assertNotIn("implicit_invocation", contract)
        self.assertTrue(contract["requires_explicit_user_request"])

    def test_openai_policy_is_derived_only_on_generated_surface(self) -> None:
        source_metadata = (
            REPO_ROOT
            / "src"
            / "skills"
            / "git"
            / "smart-commit"
            / "agents"
            / "openai.yaml"
        ).read_text(encoding="utf-8")
        generated_metadata = (
            REPO_ROOT / "skills" / "smart-commit" / "agents" / "openai.yaml"
        ).read_text(encoding="utf-8")

        self.assertNotIn("allow_implicit_invocation", source_metadata)
        self.assertIn("allow_implicit_invocation: true", generated_metadata)


if __name__ == "__main__":
    unittest.main()
