#!/usr/bin/env python3
"""Validate portable resources directly in the authored install surface."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_portability import validate_portability  # noqa: E402


def main() -> int:
    surface = REPO_ROOT / "skills"
    errors = validate_portability(surface)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Skill resource portability ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
