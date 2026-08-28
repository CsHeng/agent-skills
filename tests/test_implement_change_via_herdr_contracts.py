from __future__ import annotations

import tomllib
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class HerdrSemanticContractTests(unittest.TestCase):
    def test_public_id_is_retained_as_explicit_semantic_guidance(self) -> None:
        with (REPO_ROOT / "contracts/skills.toml").open("rb") as handle:
            entry = tomllib.load(handle)["skills"]["implement-change-via-herdr"]
        self.assertEqual("explicit", entry["activation_mode"])
        self.assertEqual(["implement-change"], entry["semantic_requires"])

    def test_skill_has_no_executable_adapter_or_persisted_protocol(self) -> None:
        root = REPO_ROOT / "skills/implement-change-via-herdr"
        text = (root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("no executable adapter", text.lower())
        self.assertIn("formal implementation review", text)
        self.assertFalse((root / "scripts").exists())
        self.assertFalse((root / "references").exists())
        for phrase in ("binding envelope", "HERDR_ENV", "lease.json", "controller-binding"):
            self.assertNotIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
