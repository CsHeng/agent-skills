"""Focused tests for the aggregate check's serial ownership boundary."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check.sh"
PRE_COMMIT = REPO_ROOT / "hooks" / "pre-commit"


class CheckOrchestrationTests(unittest.TestCase):
    def write_fake_command(self, directory: Path, name: str) -> None:
        command = directory / name
        command.write_text(
            "#!/usr/bin/env bash\n"
            "set -euo pipefail\n"
            f'printf \'{name}:%s\\n\' "$*" >> "$ORCHESTRATION_LOG"\n'
            'printf \'cache:%s|%s|%s|%s|%s\\n\' "$UV_CACHE_DIR" '
            '"$UV_PROJECT_ENVIRONMENT" "$RUFF_CACHE_DIR" "$PYTHONPYCACHEPREFIX" '
            '"$PYTEST_CACHE_DIR" >> "$ORCHESTRATION_LOG"\n'
            'if [[ "${FAKE_FAIL_MATCH:-}" == "$*" ]]; then\n'
            "  exit 23\n"
            "fi\n",
            encoding="utf-8",
        )
        command.chmod(0o755)

    def run_check(
        self, temporary: Path, *, fail_match: str = ""
    ) -> subprocess.CompletedProcess[str]:
        fake_bin = temporary / "bin"
        fake_bin.mkdir()
        self.write_fake_command(fake_bin, "python3")
        self.write_fake_command(fake_bin, "uv")
        env = os.environ | {
            "HOME": str(temporary / "home"),
            "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
            "ORCHESTRATION_LOG": str(temporary / "commands.log"),
            "FAKE_FAIL_MATCH": fail_match,
            "CHECK_PYTHON": str(fake_bin / "python3"),
            "CHECK_UV": str(fake_bin / "uv"),
        }
        (temporary / "home").mkdir()
        return subprocess.run(
            ["bash", str(CHECK_SCRIPT)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )

    def temporary_directory(self) -> tempfile.TemporaryDirectory[str]:
        root = Path(os.environ.get("TMPDIR", tempfile.gettempdir()))
        root.mkdir(parents=True, exist_ok=True)
        return tempfile.TemporaryDirectory(dir=root)

    def test_check_invokes_each_owned_gate_once_in_serial_order(self) -> None:
        with self.subTest("strict shell"):
            self.assertIn("set -euo pipefail", CHECK_SCRIPT.read_text(encoding="utf-8"))
        with self.subTest("orchestration"):
            with self.temporary_directory() as directory:
                temporary = Path(directory)
                result = self.run_check(temporary)
                self.assertEqual(0, result.returncode, result.stderr)
                log = (temporary / "commands.log").read_text(encoding="utf-8").splitlines()
                commands = [line for line in log if not line.startswith("cache:")]
                self.assertEqual(
                    [
                        "python3:scripts/check-contracts.py",
                        "python3:scripts/flatten-skills.py --target root-flat --check",
                        "python3:scripts/check-install-surface.py",
                        "python3:scripts/generate-skills-index.py --check",
                        "python3:scripts/generate-workflow-diagrams.py --check",
                        "uv:run ruff check src/runtime/harness scripts/skill_distribution.py "
                        "scripts/flatten-skills.py scripts/check-install-surface.py",
                        "uv:run ty check src/runtime/harness scripts/skill_distribution.py "
                        "scripts/flatten-skills.py scripts/check-install-surface.py",
                        "uv:run pytest -o cache_dir="
                        f"{temporary / 'home/.cache/pytest/market-csheng-harness'}",
                        "python3:src/skills/disciplines/organize-docs/scripts/"
                        "normalize-markdown-prose.py "
                        f"--root {REPO_ROOT} --immutable-manifest "
                        "contracts/markdown-prose.toml --mode check",
                    ],
                    commands,
                )
                expected_cache = (
                    f"cache:{temporary / 'home/.cache/uv/market-csheng-harness'}|"
                    f"{temporary / 'home/.cache/uv-projects/market-csheng-harness'}|"
                    f"{temporary / 'home/.cache/ruff/market-csheng-harness'}|"
                    f"{temporary / 'home/.cache/python/market-csheng-harness'}|"
                    f"{temporary / 'home/.cache/pytest/market-csheng-harness'}"
                )
                self.assertEqual(
                    [expected_cache] * 9, [line for line in log if line.startswith("cache:")]
                )

    def test_first_failed_gate_preserves_exit_status_without_later_work(self) -> None:
        with self.temporary_directory() as directory:
            temporary = Path(directory)
            result = self.run_check(
                temporary, fail_match="scripts/generate-skills-index.py --check"
            )
            self.assertEqual(23, result.returncode)
            self.assertIn("check: index", result.stderr)
            commands = (temporary / "commands.log").read_text(encoding="utf-8")
            self.assertIn("python3:scripts/check-contracts.py", commands)
            self.assertIn("python3:scripts/generate-skills-index.py --check", commands)
            self.assertNotIn("generate-workflow-diagrams.py", commands)
            self.assertNotIn("uv:run", commands)

    def test_pre_commit_is_a_non_mutating_check_entrypoint(self) -> None:
        text = PRE_COMMIT.read_text(encoding="utf-8")
        self.assertIn("set -euo pipefail", text)
        self.assertIn('exec bash "$repo_root/scripts/check.sh"', text)
        self.assertNotIn("git add", text)
        self.assertNotIn("generate-workflow-diagrams.py", text)


if __name__ == "__main__":
    unittest.main()
