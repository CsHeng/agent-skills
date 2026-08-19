#!/usr/bin/env python3
"""Validate exact root-flat parity and independently copied runtime owners."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_distribution import (  # noqa: E402, I001
    RUNTIME_OWNERS,
    compare_trees,
    render_surface,
    validate_portability,
)



def standalone_errors(surface: Path) -> list[str]:
    """Exercise each runtime owner after copying it away from the repository."""
    errors: list[str] = []
    with tempfile.TemporaryDirectory(prefix="skill-standalone-") as temporary:
        root = Path(temporary)
        for skill_id in sorted(RUNTIME_OWNERS):
            copied = root / skill_id
            shutil.copytree(surface / skill_id, copied)
            result = subprocess.run(
                [sys.executable, str(copied / "scripts" / "harness" / "cli.py"), "--help"],
                cwd=root,
                text=True,
                capture_output=True,
                check=False,
                env={"PATH": "/usr/bin:/bin:/usr/sbin:/sbin"},
            )
            if result.returncode != 0:
                errors.append(f"{skill_id}: standalone CLI failed: {result.stderr.strip()}")
    return errors


def main() -> int:
    surface = REPO_ROOT / "skills"
    with tempfile.TemporaryDirectory(prefix="skill-expected-", dir=REPO_ROOT) as temporary:
        expected = Path(temporary) / "skills"
        render_surface(REPO_ROOT, expected)
        errors = [*compare_trees(expected, surface), *validate_portability(surface)]
    if not errors:
        errors.extend(standalone_errors(surface))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("root-flat install surface ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
