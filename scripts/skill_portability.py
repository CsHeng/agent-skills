#!/usr/bin/env python3
"""Check portable Skill resources without generating an installation tree."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

PROVIDER_ROOTS = (
    "$PLUGIN_ROOT",
    "${PLUGIN_ROOT",
    "$CLAUDE_PLUGIN_ROOT",
    "${CLAUDE_PLUGIN_ROOT",
)
INLINE_LINK = re.compile(r'\[[^\]\n]*\]\((?:<([^>\n]+)>|([^\s)]+))(?:\s+"[^"]*")?\)')
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]\n]+\]:\s*<?([^\s>]+)>?", re.MULTILINE)


def _markdown_prose(content: str) -> str:
    lines: list[str] = []
    fence = ""
    for line in content.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            value = marker[1]
            if not fence:
                fence = value
            elif value[0] == fence[0] and len(value) >= len(fence):
                fence = ""
            continue
        if not fence:
            lines.append(line)
    return "\n".join(lines)


def _local_link_errors(path: Path, skill_dir: Path, content: str) -> list[str]:
    prose = _markdown_prose(content)
    targets = [match[1] or match[2] for match in INLINE_LINK.finditer(prose)]
    targets.extend(match[1] for match in REFERENCE_LINK.finditer(prose))
    errors: list[str] = []
    for target in targets:
        parsed = urlsplit(target)
        if parsed.scheme and parsed.scheme != "file" or parsed.netloc:
            continue
        if not parsed.path:
            continue
        resource = (path.parent / unquote(parsed.path)).resolve()
        if not resource.is_relative_to(skill_dir.resolve()):
            errors.append(f"resource link leaves the Skill directory: {target}")
        elif not resource.exists():
            errors.append(f"resource link does not exist: {target}")
    return errors


def validate_portability(surface: Path) -> list[str]:
    """Check provider independence and linked resource closure for each Skill."""
    if not surface.is_dir():
        return [f"Skill directory does not exist: {surface}"]
    errors: list[str] = []
    for skill_dir in sorted(surface.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.is_symlink():
            errors.append(f"{skill_dir.name}: authored Skill directory is a symlink")
            continue
        for path in sorted(skill_dir.rglob("*")):
            relative = path.relative_to(surface).as_posix()
            if path.is_symlink():
                if not path.resolve().is_relative_to(skill_dir.resolve()):
                    errors.append(
                        f"{relative}: resource symlink leaves the Skill directory"
                    )
                    continue
                if not path.exists():
                    errors.append(f"{relative}: resource symlink target does not exist")
                    continue
            if not path.is_file():
                continue
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for token in PROVIDER_ROOTS:
                if token in content:
                    errors.append(f"{relative}: assumes provider root {token}")
            if path.suffix.lower() == ".md":
                errors.extend(
                    f"{relative}: {error}"
                    for error in _local_link_errors(path, skill_dir, content)
                )
    return errors
