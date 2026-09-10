"""Behavioral contracts for repository formatting policy and Ruff config."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LONG_PAYLOAD = "preserve this exact multiword payload " * 8
CLEAN_SOURCE = f'PAYLOAD = "{LONG_PAYLOAD}"\n'
SEMANTIC_LINT_SOURCE = f"import json\n\n{CLEAN_SOURCE}"


def string_constants(source: str) -> list[str]:
    values: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
    return values


def run_ruff(*args: str, stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "ruff",
            *args,
            "--config",
            str(REPO_ROOT / "pyproject.toml"),
            "--no-cache",
        ],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        input=stdin,
        env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"},
    )


class FormattingPolicyContractTests(unittest.TestCase):
    def test_repo_ruff_config_has_no_line_length_or_e501_gate(self) -> None:
        with (REPO_ROOT / "pyproject.toml").open("rb") as handle:
            data = tomllib.load(handle)
        ruff = data["tool"]["ruff"]
        lint = ruff["lint"]

        self.assertNotIn("line-length", ruff)
        self.assertNotIn("line-length", lint)
        self.assertEqual(["E", "F", "I", "UP", "B"], lint["select"])
        self.assertEqual(["E501"], lint["ignore"])
        self.assertGreater(len(LONG_PAYLOAD), 100)

    def test_long_string_survives_format_then_passes_lint(self) -> None:
        formatted = run_ruff(
            "format",
            "--stdin-filename",
            "sample.py",
            "-",
            stdin=CLEAN_SOURCE,
        )
        self.assertEqual(0, formatted.returncode, formatted.stderr)
        self.assertEqual(
            ast.dump(ast.parse(CLEAN_SOURCE)), ast.dump(ast.parse(formatted.stdout))
        )

        lint = run_ruff(
            "check",
            "--stdin-filename",
            "sample.py",
            "-",
            stdin=formatted.stdout,
        )
        self.assertEqual(0, lint.returncode, lint.stdout + lint.stderr)
        self.assertNotIn("E501", lint.stdout + lint.stderr)

        strict = run_ruff(
            "check",
            "--select",
            "E501",
            "--config",
            "lint.ignore = []",
            "--stdin-filename",
            "sample.py",
            "-",
            stdin=formatted.stdout,
        )
        self.assertEqual(1, strict.returncode, strict.stdout + strict.stderr)
        self.assertIn("E501", strict.stdout)

    def test_documented_fix_format_sequence_preserves_exit_boundaries(self) -> None:
        skill = (
            REPO_ROOT / "src/skills/policies/python-guidelines/SKILL.md"
        ).read_text(encoding="utf-8")
        commands = skill.split("## Operational Commands (Examples)", 1)[1]
        script = commands.split("```bash\n", 1)[1].split("```", 1)[0]
        fake_uv = """uv() {
  printf '%s\\n' "$*" >> "$TRACE_FILE"
  case "$*" in
    *"ruff check --fix "*) return "$FIX_EXIT" ;;
    *"ruff format --check "*) return "$FORMAT_CHECK_EXIT" ;;
    *"ruff format "*) return "$FORMAT_EXIT" ;;
    *"ruff check "*) return "$CHECK_EXIT" ;;
    *) return 0 ;;
  esac
}
"""
        cases = (
            (1, 0, 0, 0, 0, 6),
            (2, 0, 0, 0, 2, 1),
            (0, 2, 0, 0, 2, 2),
            (1, 0, 1, 0, 1, 3),
            (0, 0, 0, 1, 1, 4),
        )
        for fix, formatter, lint, format_check, expected_exit, expected_calls in cases:
            with self.subTest(
                fix=fix, formatter=formatter, lint=lint, format_check=format_check
            ):
                with tempfile.TemporaryDirectory() as temporary:
                    trace = Path(temporary) / "calls.txt"
                    result = subprocess.run(
                        ["bash", "-c", fake_uv + script],
                        cwd=temporary,
                        capture_output=True,
                        text=True,
                        check=False,
                        env=os.environ
                        | {
                            "HOME": temporary,
                            "TRACE_FILE": str(trace),
                            "FIX_EXIT": str(fix),
                            "FORMAT_EXIT": str(formatter),
                            "CHECK_EXIT": str(lint),
                            "FORMAT_CHECK_EXIT": str(format_check),
                        },
                    )
                    self.assertEqual(expected_exit, result.returncode, result.stderr)
                    calls = trace.read_text(encoding="utf-8").splitlines()
                    self.assertEqual(expected_calls, len(calls), calls)
                    self.assertIn("--no-unsafe-fixes", calls[0])
                    if len(calls) > 1:
                        self.assertIn("ruff format -- path/to/changed.py", calls[1])

    def test_semantic_lint_still_fails_under_repo_config(self) -> None:
        formatted = run_ruff(
            "format",
            "--stdin-filename",
            "sample.py",
            "-",
            stdin=SEMANTIC_LINT_SOURCE,
        )
        self.assertEqual(0, formatted.returncode, formatted.stderr)
        self.assertIn(LONG_PAYLOAD, string_constants(formatted.stdout))

        lint = run_ruff(
            "check",
            "--stdin-filename",
            "sample.py",
            "-",
            stdin=formatted.stdout,
        )
        combined = lint.stdout + lint.stderr
        self.assertEqual(1, lint.returncode, combined)
        self.assertIn("F401", combined)
        self.assertNotIn("E501", combined)


if __name__ == "__main__":
    unittest.main()
