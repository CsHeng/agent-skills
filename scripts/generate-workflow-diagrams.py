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
    "skill-composition": """@startuml
title Portable Skill composition
top to bottom direction
rectangle "Compatible agent host\n(loop, tools, session)" as host
rectangle "Active coding agent\n(selection and judgment)" as agent
rectangle "Primary Skill" as primary
rectangle "Session overlay" as session
rectangle "Discipline / policy overlay" as policy
rectangle "Tool Skill" as tool
rectangle "Optional read-only review evaluator" as evaluator
rectangle "One semantic result" as result
host --> agent : request and capabilities
agent --> primary : select
session ..> primary
policy ..> primary
tool ..> primary
evaluator ..> agent : candidate findings
primary --> result
result --> agent : evidence
note right of result
No fixed phase, runtime mode, or implicit review.
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
