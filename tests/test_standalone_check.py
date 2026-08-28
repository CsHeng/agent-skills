from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts/run-standalone-check.py"


class StandaloneCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("standalone_check", SCRIPT)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load standalone check")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_copy_excludes_local_stage_and_execution_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "copy"
            destination.mkdir()
            self.module.copy_repository(REPO_ROOT, destination)
            self.assertTrue((destination / "skills.index.json").is_file())
            for relative in (".git", ".dist", ".pi", ".venv", "docs/plans", "integrations", "src/runtime"):
                self.assertFalse((destination / relative).exists(), relative)
            self.assertEqual(self.module.surface_digest(destination), self.module.surface_digest(destination))

    def test_run_redacts_output_and_propagates_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            command = root / "fail"
            command.write_text("#!/usr/bin/env sh\nprintf 'secret-output' >&2\nexit 23\n")
            command.chmod(0o755)
            with self.assertRaisesRegex(RuntimeError, r"check failed: .* \(23\)") as raised:
                self.module.run([str(command)], root, {"PATH": os.environ["PATH"]})
            self.assertNotIn("secret-output", str(raised.exception))

    def test_script_contains_provider_isolation_and_cleanup_boundary(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("TemporaryDirectory", text)
        self.assertIn("PI_CONFIG_DIR", text)
        self.assertIn("PI_CODING_AGENT_DIR", text)
        self.assertIn('"HOME": str(isolated_home)', text)
        self.assertIn('"XDG_CACHE_HOME": str(root / "cache")', text)
        self.assertIn("exit 97", text)
        self.assertNotIn("CODEX_HOME", text)


if __name__ == "__main__":
    unittest.main()
