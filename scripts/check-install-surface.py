#!/usr/bin/env python3
"""Validate exact root-flat parity and portable generated Skills."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_distribution import (  # noqa: E402
    compare_trees,
    render_surface,
    validate_portability,
)


def main() -> int:
    surface = REPO_ROOT / "skills"
    with tempfile.TemporaryDirectory(prefix="skill-expected-", dir=REPO_ROOT) as temporary:
        expected = Path(temporary) / "skills"
        render_surface(REPO_ROOT, expected)
        errors = [*compare_trees(expected, surface), *validate_portability(surface)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("root-flat install surface ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
