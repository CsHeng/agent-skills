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
            REPO_ROOT / "scripts" / "generate-workflow-diagrams.py",
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("failed to load diagram generator")
        cls.generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.generator)

    def test_trigger_ownership_view_is_contract_derived(self) -> None:
        outputs = self.generator.expected_outputs()
        trigger_path = (
            REPO_ROOT
            / "docs"
            / "architecture"
            / "diagrams"
            / "skill-trigger-ownership.puml"
        )

        self.assertIn(trigger_path, outputs)
        content = outputs[trigger_path]
        for mode in ("native", "conditional", "controller", "explicit", "baseline"):
            self.assertIn(f"Activation: {mode}", content)
        self.assertIn("superseded_by", content)
        self.assertIn("case owner", content)
        self.assertIn("controller evaluator", content)
        self.assertIn("rendering baseline", content)
        self.assertNotIn("lexical_hints", content)
        self.assertNotIn("architecture drift", content)


if __name__ == "__main__":
    unittest.main()
