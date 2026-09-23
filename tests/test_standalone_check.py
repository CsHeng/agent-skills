from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

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

    def test_main_isolates_children_and_cleans_up_on_success_or_failure(self) -> None:
        for fails in (False, True):
            with self.subTest(fails=fails):
                environments: list[dict[str, str]] = []

                def capture_run(
                    command: list[str], cwd: Path, env: dict[str, str],
                    *, should_fail: bool = fails, observed: list[dict[str, str]] = environments,
                ) -> None:
                    observed.append(env.copy())
                    self.assertTrue((cwd.parent / "bin" / "pi").is_file())
                    if should_fail:
                        raise RuntimeError("fixture check failed")

                output = io.StringIO()
                with (
                    patch.object(self.module, "copy_repository") as copy,
                    patch.object(self.module, "run", side_effect=capture_run),
                    patch.dict(os.environ, {"CODEX_HOME": "ambient-secret", "PI_API_KEY": "ambient-secret"}),
                    redirect_stdout(output),
                ):
                    status = self.module.main()
                root = copy.call_args.args[1].parent
                report = json.loads(output.getvalue())
                self.assertEqual(status, 1 if fails else 0)
                self.assertTrue(report["pi_blocked"])
                self.assertEqual(report["checks"], "pending" if fails else "pass")
                self.assertTrue(environments)
                for env in environments:
                    self.assertEqual(
                        set(env),
                        {"HOME", "PATH", "TMPDIR", "XDG_CACHE_HOME", "PI_CONFIG_DIR", "PI_CODING_AGENT_DIR", "STANDALONE_CHECK_ACTIVE", "PYTHONDONTWRITEBYTECODE"},
                    )
                    self.assertEqual(env["HOME"], str(root / "home"))
                    self.assertEqual(env["XDG_CACHE_HOME"], str(root / "cache"))
                    self.assertEqual(env["PI_CONFIG_DIR"], env["PI_CODING_AGENT_DIR"])
                    self.assertEqual(env["PI_CONFIG_DIR"], str(root / "pi-config"))
                    self.assertEqual(env["TMPDIR"], str(root / "tmp"))
                    self.assertEqual(env["PATH"].split(os.pathsep)[0], str(root / "bin"))
                self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()
