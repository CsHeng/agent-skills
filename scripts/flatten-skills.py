#!/usr/bin/env python3
"""Generate or check the sole tracked root-flat skill surface."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_distribution import (  # noqa: E402, I001
    DistributionError,
    build_validated_surface,
    compare_trees,
    replace_directory,
)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["root-flat"], required=True)
    parser.add_argument("--dest", type=Path, help="Override the root-flat destination")
    parser.add_argument("--check", action="store_true", help="Fail when generated output is stale")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    destination = (REPO_ROOT / args.dest).resolve() if args.dest else REPO_ROOT / "skills"
    temporary, staged = build_validated_surface(REPO_ROOT, destination.parent)
    try:
        if args.check:
            errors = (
                compare_trees(staged, destination) if destination.is_dir() else ["skills missing"]
            )
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            return 0
        replace_directory(staged, destination)
        return 0
    finally:
        shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except DistributionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1) from error
