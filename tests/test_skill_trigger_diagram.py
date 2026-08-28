from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class SkillTriggerDiagramTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location(
            "generate_workflow_diagrams",
            REPO_ROOT / "scripts/generate-workflow-diagrams.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("failed to load diagram generator")
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)

    def test_diagrams_show_semantic_composition_only(self) -> None:
        self.assertEqual({"semantic-workflow", "skill-composition"}, set(self.generator.DIAGRAMS))
        content = "\n".join(self.generator.DIAGRAMS.values())
        self.assertIn("exactly one review", content)
        self.assertIn("Informal work has no implied review", content)
        self.assertIn("Standalone review", content)
        for mechanical in ("ledger", "attempt", "replay", "scheduler", "provider adapter"):
            self.assertNotIn(mechanical, content.lower())


if __name__ == "__main__":
    unittest.main()
