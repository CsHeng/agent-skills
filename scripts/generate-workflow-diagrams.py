#!/usr/bin/env python3
"""Generate semantic Skill-composition diagrams."""

from __future__ import annotations

import argparse
import sys
from html import escape
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "docs/architecture/diagrams"
SVG_DIR = REPO_ROOT / "docs/architecture/generated"
DIAGRAMS = {
    "semantic-workflow": """@startuml
title Semantic workflow composition
left to right direction
rectangle "analyze-project" as analyze
rectangle "design-change" as design
rectangle "plan-change" as plan
rectangle "implement-change" as impl
rectangle "review-change\n(read-only bounded review)" as review
rectangle "sync-truth" as truth
rectangle "close-change" as close
analyze --> design : relevant truth
design --> plan : approved design
plan --> impl : approved plan
design ..> review : exactly one review
plan ..> review : exactly one review
impl ..> review : exactly one review
impl --> truth : verified truth impact
truth --> close : stable truth current
impl --> close : no truth impact
note bottom of review
Standalone review starts from one supplied target.
Informal work has no implied review.
end note
@enduml
""",
    "skill-composition": """@startuml
title Portable Skill composition
top to bottom direction
rectangle "Primary workflow Skill" as primary
rectangle "Session overlay" as session
rectangle "Discipline / policy overlay" as policy
rectangle "Tool Skill" as tool
rectangle "Read-only review evaluator" as evaluator
rectangle "One semantic result" as result
session ..> primary
policy ..> primary
tool ..> primary
evaluator ..> primary : candidate findings
primary --> result
note right of result
No environment-specific execution contract.
end note
@enduml
""",
}


def render_svg(source: str) -> bytes:
    lines = [
        line.strip().replace('rectangle "', "").replace('" as ', " [") + ("]" if '" as ' in line else "")
        for line in source.splitlines()
        if line.strip().startswith(("title ", "rectangle ", "note ")) or " --> " in line or " ..> " in line
    ]
    height = 44 + 24 * len(lines)
    rows = "".join(
        f'<text x="20" y="{32 + index * 24}" font-family="sans-serif" font-size="14">{escape(line)}</text>'
        for index, line in enumerate(lines)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}">'
        '<rect width="100%" height="100%" fill="white" stroke="#555"/>'
        f"{rows}</svg>\n"
    ).encode()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    SVG_DIR.mkdir(parents=True, exist_ok=True)
    for name, source in DIAGRAMS.items():
        puml = SOURCE_DIR / f"{name}.puml"
        svg = SVG_DIR / f"{name}.svg"
        rendered = render_svg(source)
        if args.check:
            if not puml.is_file() or puml.read_text(encoding="utf-8") != source:
                errors.append(f"stale diagram source: {puml.relative_to(REPO_ROOT)}")
            if not svg.is_file() or svg.read_bytes() != rendered:
                errors.append(f"stale diagram rendering: {svg.relative_to(REPO_ROOT)}")
        else:
            puml.write_text(source, encoding="utf-8")
            svg.write_bytes(rendered)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
