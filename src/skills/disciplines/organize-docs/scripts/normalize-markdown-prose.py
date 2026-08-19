#!/usr/bin/env python3
"""Detect and remove fixed-width Markdown prose wrapping."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PREVIEW_LIMIT = 50
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
}
IMMUTABLE_MANIFEST_VERSION = 1
SHA256_RE = re.compile(r"[0-9a-f]{64}")
GLOB_CHARACTERS = frozenset("*?[]{}!")

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
SETEXT_RE = re.compile(r"^\s{0,3}(?:=+|-+)\s*$")
THEMATIC_RE = re.compile(r"^\s{0,3}([-*_])(?:\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^(\s*)([-+*]|\d+[.)])(\s+)(.*)$")
BLOCKQUOTE_RE = re.compile(r"^(\s{0,3}(?:>[ \t]?)+)(.*)$")
DEFINITION_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s+")
HTML_ONLY_RE = re.compile(r"^\s{0,3}</?[A-Za-z][^>]*>\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
DIRECTIVE_RE = re.compile(
    r"^\s*(?:"
    r"REQUIRED|PREFERRED|PROHIBITED|OPTIONAL|SUCCESS|ERROR|WARNING|INFO"
    r"):\s+"
)
KEY_VALUE_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9 _/-]{0,48}:\s+")
BOLD_KEY_VALUE_RE = re.compile(r"^\s*\*\*[^*]+:\*\*\s+")
KEY_ONLY_RE = re.compile(r"^\s*[A-Za-z_][A-Za-z0-9 _/-]{0,48}:\s*$")
BOLD_KEY_ONLY_RE = re.compile(r"^\s*\*\*[^*]+:\*\*\s*$")
INSTRUCTION_RE = re.compile(
    r"^\s*(?:"
    r"Step\s+\d+(?:\.\d+)?\s+[—-]|"
    r"[a-z]\)\s+|"
    r"If\s+|Otherwise,|Run:|Record\s+|Try in order:|"
    r"Use\s+the\s+resolved|Invoke\s+the\s+Bash tool|Build\s+`args`|"
    r"Extract\s+the\s+JSON|Before\s+reporting|This is\s+the\s+"
    r")"
)
CJK_RE = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
EXPLICIT_HTML_BREAK_RE = re.compile(r"<br\s*/?>\s*$", re.IGNORECASE)


class MarkdownNormalizationError(RuntimeError):
    """Raised when Markdown normalization cannot proceed safely."""


@dataclass(frozen=True)
class JoinFinding:
    """One physical newline that can be replaced with natural-line spacing."""

    line_number: int
    following_line_number: int
    first_text: str
    following_text: str


@dataclass(frozen=True)
class TransformResult:
    """Normalized text and the joins used to produce it."""

    text: str
    findings: tuple[JoinFinding, ...]

    @property
    def join_count(self) -> int:
        """Return the number of removed prose continuation breaks."""

        return len(self.findings)


@dataclass(frozen=True)
class FileAnalysis:
    """Source and transform result for one Markdown file."""

    file_path: Path
    source_text: str
    result: TransformResult


@dataclass(frozen=True)
class ImmutableException:
    """One pinned stage-history file excluded from Markdown rewrite mode."""

    relative_path: Path
    sha256: str


@dataclass
class PendingParagraph:
    """Mutable paragraph state while parsing one Markdown document."""

    rendered: str
    last_source_text: str
    last_line_number: int
    kind: str
    quote_depth: int | None = None


def table_line_numbers(lines: list[str]) -> set[int]:
    """Return zero-based line indexes belonging to Markdown tables."""

    table_lines: set[int] = set()
    for index, line in enumerate(lines):
        quote_depth, content = blockquote_content(line)
        if not TABLE_SEPARATOR_RE.match(content.strip()):
            continue
        start = index
        while start > 0:
            previous_depth, previous_content = blockquote_content(lines[start - 1])
            if (
                previous_depth != quote_depth
                or "|" not in previous_content
                or not previous_content.strip()
            ):
                break
            start -= 1
        end = index
        while end + 1 < len(lines):
            following_depth, following_content = blockquote_content(lines[end + 1])
            if (
                following_depth != quote_depth
                or "|" not in following_content
                or not following_content.strip()
            ):
                break
            end += 1
        table_lines.update(range(start, end + 1))
    return table_lines


def setext_line_numbers(lines: list[str], table_lines: set[int]) -> set[int]:
    """Return indexes for Setext heading text and underline lines."""

    setext_lines: set[int] = set()
    for index, line in enumerate(lines):
        quote_depth, content = blockquote_content(line)
        if index == 0 or index in table_lines or not SETEXT_RE.match(content):
            continue
        previous_depth, previous_content = blockquote_content(lines[index - 1])
        if previous_depth == quote_depth and previous_content.strip():
            setext_lines.update({index - 1, index})
    return setext_lines


def is_semantic_line_start(line: str) -> bool:
    """Return whether a line starts a repository-style standalone statement."""

    return bool(
        DIRECTIVE_RE.match(line)
        or KEY_VALUE_RE.match(line)
        or BOLD_KEY_VALUE_RE.match(line)
        or INSTRUCTION_RE.match(line)
    )


def is_empty_semantic_line(line: str) -> bool:
    """Return whether a line is a standalone metadata field without a value."""

    return bool(KEY_ONLY_RE.match(line) or BOLD_KEY_ONLY_RE.match(line))


def has_explicit_hard_break(line: str) -> bool:
    """Return whether Markdown syntax requires the next physical line."""

    return line.endswith(("  ", "\\")) or bool(EXPLICIT_HTML_BREAK_RE.search(line))


def blockquote_content(line: str) -> tuple[int, str]:
    """Return blockquote depth and content after its quote markers."""

    match = BLOCKQUOTE_RE.match(line)
    if match is None:
        return 0, line
    quote_prefix, content = match.groups()
    return quote_prefix.count(">"), content


def join_fragments(left: str, right: str) -> str:
    """Join two prose fragments without fixed-width wrapping."""

    left_text = left.rstrip()
    right_text = right.strip()
    if not left_text:
        return right_text
    if not right_text:
        return left_text
    if left_text.endswith("-") and right_text[0].islower():
        return left_text + right_text
    if CJK_RE.search(left_text[-1]) and CJK_RE.match(right_text[0]):
        return left_text + right_text
    return f"{left_text} {right_text}"


def semantic_fingerprint(text: str) -> str:
    """Return non-whitespace content while ignoring blockquote syntax prefixes."""

    content_lines = [
        BLOCKQUOTE_RE.sub(lambda match: match.group(2), line, count=1)
        for line in text.splitlines()
    ]
    return re.sub(r"\s+", "", "\n".join(content_lines))


def structure_fingerprint(text: str) -> tuple[int, int, int, int]:
    """Return counts for structures that normalization must preserve."""

    lines = text.splitlines()
    return (
        sum(1 for line in lines if FENCE_RE.match(blockquote_content(line)[1])),
        sum(1 for line in lines if HEADING_RE.match(blockquote_content(line)[1])),
        sum(
            1 for line in lines if TABLE_SEPARATOR_RE.match(blockquote_content(line)[1])
        ),
        sum(1 for line in lines if LIST_RE.match(blockquote_content(line)[1])),
    )


def validate_transform(source: str, result: str) -> None:
    """Reject a transform that changes content or Markdown block counts."""

    if semantic_fingerprint(source) != semantic_fingerprint(result):
        raise MarkdownNormalizationError(
            "normalization changed non-whitespace Markdown prose content"
        )
    if structure_fingerprint(source) != structure_fingerprint(result):
        raise MarkdownNormalizationError(
            "normalization changed fence, heading, table, or list structure"
        )


def transform_markdown(source: str) -> TransformResult:
    """Return Markdown with natural paragraphs and list items on physical lines."""

    final_newline = source.endswith(("\n", "\r"))
    newline = "\r\n" if "\r\n" in source else "\n"
    lines = source.splitlines()
    table_lines = table_line_numbers(lines)
    setext_lines = setext_line_numbers(lines, table_lines)
    output: list[str] = []
    findings: list[JoinFinding] = []
    pending: PendingParagraph | None = None
    frontmatter_marker = lines[0].strip() if lines else ""
    frontmatter_closers = {
        "---": {"---", "..."},
        "+++": {"+++"},
    }.get(frontmatter_marker)
    frontmatter_end = (
        next(
            (
                index
                for index, line in enumerate(lines[1:], start=1)
                if line.strip() in frontmatter_closers
            ),
            None,
        )
        if frontmatter_closers is not None
        else None
    )
    in_html_comment = False
    fence_stack: list[tuple[str, int, int]] = []

    def flush_pending() -> None:
        nonlocal pending
        if pending is not None:
            output.append(pending.rendered)
            pending = None

    def start_pending(
        line: str,
        line_number: int,
        kind: str,
        quote_depth: int | None = None,
    ) -> None:
        nonlocal pending
        pending = PendingParagraph(
            rendered=line,
            last_source_text=line,
            last_line_number=line_number,
            kind=kind,
            quote_depth=quote_depth,
        )

    def append_continuation(line: str, line_number: int, content: str) -> None:
        if pending is None:
            raise MarkdownNormalizationError("missing paragraph state")
        findings.append(
            JoinFinding(
                line_number=pending.last_line_number,
                following_line_number=line_number,
                first_text=pending.last_source_text,
                following_text=line,
            )
        )
        pending.rendered = join_fragments(pending.rendered, content)
        pending.last_source_text = line
        pending.last_line_number = line_number

    for index, line in enumerate(lines):
        line_number = index + 1
        stripped = line.strip()
        quote_depth, quote_content = blockquote_content(line)
        structural_content = quote_content if quote_depth else line

        if frontmatter_end is not None and index <= frontmatter_end:
            flush_pending()
            output.append(line)
            continue

        fence_match = FENCE_RE.match(quote_content)
        if fence_stack:
            flush_pending()
            output.append(line)
            if fence_match:
                fence_token = fence_match.group(1)
                fence_suffix = quote_content[fence_match.end() :].strip()
                (
                    current_character,
                    current_length,
                    current_quote_depth,
                ) = fence_stack[-1]
                if (
                    quote_depth == current_quote_depth
                    and not fence_suffix
                    and fence_token[0] == current_character
                    and len(fence_token) >= current_length
                ):
                    fence_stack.pop()
                elif quote_depth == current_quote_depth and fence_suffix:
                    fence_stack.append((fence_token[0], len(fence_token), quote_depth))
            continue
        if fence_match:
            flush_pending()
            output.append(line)
            fence_token = fence_match.group(1)
            fence_stack.append((fence_token[0], len(fence_token), quote_depth))
            continue

        if in_html_comment:
            flush_pending()
            output.append(line)
            if "-->" in structural_content:
                in_html_comment = False
            continue
        if "<!--" in structural_content and "-->" not in structural_content:
            flush_pending()
            output.append(line)
            in_html_comment = True
            continue

        if pending is not None and has_explicit_hard_break(pending.last_source_text):
            flush_pending()

        if (
            not stripped
            or index in table_lines
            or index in setext_lines
            or HEADING_RE.match(structural_content)
            or THEMATIC_RE.match(structural_content)
            or DEFINITION_RE.match(structural_content)
            or HTML_ONLY_RE.match(structural_content)
            or (
                is_empty_semantic_line(structural_content)
                and (pending is None or pending.kind != "prose")
            )
            or (quote_depth and re.match(r"^(?: {4,}|\t)\S", structural_content))
        ):
            flush_pending()
            output.append(line)
            continue

        if quote_depth:
            if not quote_content.strip():
                flush_pending()
                output.append(line)
                continue
            quote_is_list = bool(LIST_RE.match(quote_content))
            quote_is_semantic = is_semantic_line_start(quote_content)
            if (
                pending is not None
                and pending.kind == "quote"
                and pending.quote_depth == quote_depth
                and not quote_is_list
                and not quote_is_semantic
            ):
                append_continuation(line, line_number, quote_content)
            else:
                flush_pending()
                start_pending(line, line_number, "quote", quote_depth)
            continue

        list_match = LIST_RE.match(line)
        if list_match:
            flush_pending()
            list_content = list_match.group(4)
            list_kind = (
                "list-metadata"
                if is_semantic_line_start(list_content)
                or is_empty_semantic_line(list_content)
                else "list"
            )
            start_pending(line, line_number, list_kind)
            continue

        if is_semantic_line_start(line):
            if pending is not None and pending.kind == "list":
                append_continuation(line, line_number, line)
                continue
            flush_pending()
            start_pending(line, line_number, "semantic")
            continue

        if re.match(r"^(?: {4,}|\t)\S", line) and (
            pending is None or pending.kind != "list"
        ):
            flush_pending()
            output.append(line)
            continue

        if pending is None:
            start_pending(line, line_number, "prose")
        else:
            append_continuation(line, line_number, line)

    flush_pending()
    normalized = newline.join(output)
    if final_newline:
        normalized += newline
    validate_transform(source, normalized)
    return TransformResult(text=normalized, findings=tuple(findings))


def discover_markdown_files(root: Path) -> list[Path]:
    """Return Git-visible Markdown files, or a bounded filesystem fallback."""

    resolved_root = root.expanduser().resolve(strict=True)
    try:
        completed = subprocess.run(
            [
                "git",
                "ls-files",
                "-z",
                "--cached",
                "--others",
                "--exclude-standard",
                "--",
                "*.md",
            ],
            cwd=resolved_root,
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        candidates = resolved_root.rglob("*.md")
    else:
        candidates = (
            resolved_root / item.decode("utf-8")
            for item in completed.stdout.split(b"\0")
            if item
        )
    return sorted(
        {
            candidate
            for candidate in candidates
            if candidate.exists()
            and candidate.is_file()
            and not candidate.is_symlink()
            and not any(
                part in EXCLUDED_DIRECTORY_NAMES
                for part in candidate.relative_to(resolved_root).parts
            )
        }
    )


def load_immutable_manifest(root: Path, manifest_path: Path) -> tuple[ImmutableException, ...]:
    """Load pinned, Git-visible `docs/plans` exceptions without enrollment shortcuts."""

    resolved_root = root.expanduser().resolve(strict=True)
    resolved_manifest = manifest_path.expanduser().resolve(strict=True)
    try:
        with resolved_manifest.open("rb") as handle:
            manifest = tomllib.load(handle)
    except tomllib.TOMLDecodeError as error:
        raise MarkdownNormalizationError(
            f"immutable manifest is invalid TOML: {resolved_manifest}"
        ) from error
    if set(manifest) != {"version", "exceptions"}:
        raise MarkdownNormalizationError(
            "immutable manifest allows only version and exceptions"
        )
    if manifest.get("version") != IMMUTABLE_MANIFEST_VERSION:
        raise MarkdownNormalizationError(
            f"immutable manifest version must be {IMMUTABLE_MANIFEST_VERSION}"
        )
    entries = manifest.get("exceptions")
    if not isinstance(entries, list) or not entries:
        raise MarkdownNormalizationError("immutable manifest requires non-empty exceptions")

    visible_paths = {
        markdown_file.relative_to(resolved_root)
        for markdown_file in discover_markdown_files(resolved_root)
    }
    exceptions: list[ImmutableException] = []
    seen_paths: set[Path] = set()
    seen_digests: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise MarkdownNormalizationError(
                "each immutable exception requires exactly path and sha256"
            )
        raw_path = entry["path"]
        digest = entry["sha256"]
        if not isinstance(raw_path, str) or not isinstance(digest, str):
            raise MarkdownNormalizationError(
                "immutable exception path and sha256 must be strings"
            )
        relative_path = Path(raw_path)
        if (
            relative_path.is_absolute()
            or ".." in relative_path.parts
            or any(character in raw_path for character in GLOB_CHARACTERS)
            or len(relative_path.parts) < 3
            or relative_path.parts[:2] != ("docs", "plans")
            or relative_path.suffix != ".md"
        ):
            raise MarkdownNormalizationError(
                f"immutable exception must be a literal docs/plans Markdown path: {raw_path}"
            )
        if not SHA256_RE.fullmatch(digest):
            raise MarkdownNormalizationError(
                f"immutable exception sha256 must be lowercase hexadecimal: {raw_path}"
            )
        if relative_path in seen_paths or digest in seen_digests:
            raise MarkdownNormalizationError("immutable manifest contains duplicate path or sha256")
        candidate = resolved_root / relative_path
        if (
            relative_path not in visible_paths
            or not candidate.exists()
            or not candidate.is_file()
            or candidate.is_symlink()
        ):
            raise MarkdownNormalizationError(
                f"immutable exception must be a regular Git-visible file: {raw_path}"
            )
        actual_digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if actual_digest != digest:
            raise MarkdownNormalizationError(
                f"immutable exception digest mismatch: {raw_path}"
            )
        seen_paths.add(relative_path)
        seen_digests.add(digest)
        exceptions.append(ImmutableException(relative_path, digest))
    return tuple(exceptions)


def validate_immutable_findings(
    root: Path,
    analyses: list[FileAnalysis],
    exceptions: tuple[ImmutableException, ...],
) -> None:
    """Ensure every immutable exception still protects a real legacy finding."""

    by_path = {analysis.file_path.relative_to(root): analysis for analysis in analyses}
    for exception in exceptions:
        analysis = by_path.get(exception.relative_path)
        if analysis is None or analysis.result.join_count == 0:
            raise MarkdownNormalizationError(
                "immutable exception no longer contains a preserved hard-wrap finding: "
                f"{exception.relative_path}"
            )


def analyze_repository(root: Path) -> list[FileAnalysis]:
    """Analyze every Git-visible Markdown file under a repository root."""

    analyses: list[FileAnalysis] = []
    for markdown_file in discover_markdown_files(root):
        try:
            source = markdown_file.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            raise MarkdownNormalizationError(
                f"{markdown_file} is not valid UTF-8"
            ) from error
        result = transform_markdown(source)
        analyses.append(
            FileAnalysis(
                file_path=markdown_file,
                source_text=source,
                result=result,
            )
        )
    return analyses


def write_text_atomic(file_path: Path, source: str, replacement: str) -> None:
    """Atomically replace one unchanged Markdown file while preserving its mode."""

    current = file_path.read_text(encoding="utf-8")
    if current != source:
        raise MarkdownNormalizationError(
            f"{file_path} changed after analysis; rerun before writing"
        )
    file_mode = file_path.stat().st_mode
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            prefix=f".{file_path.name}.",
            dir=file_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_file.write(replacement)
            temporary_name = temporary_file.name
        os.chmod(temporary_name, stat.S_IMODE(file_mode))
        os.replace(temporary_name, file_path)
    finally:
        if temporary_name is not None and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def mutable_analyses(
    root: Path,
    analyses: list[FileAnalysis],
    exceptions: tuple[ImmutableException, ...],
) -> list[FileAnalysis]:
    """Return analyses eligible for check output and write-mode replacement."""

    immutable_paths = {exception.relative_path for exception in exceptions}
    return [
        analysis
        for analysis in analyses
        if analysis.file_path.relative_to(root) not in immutable_paths
    ]


def print_summary(analyses: list[FileAnalysis]) -> None:
    """Print deterministic repository-level normalization counts."""

    affected = [analysis for analysis in analyses if analysis.result.join_count > 0]
    print(f"markdown_files={len(analyses)}")
    print(f"files_with_hard_wrap={len(affected)}")
    print(f"join_count={sum(analysis.result.join_count for analysis in affected)}")


def print_preview(root: Path, analyses: list[FileAnalysis], limit: int) -> None:
    """Print bounded candidate joins for review."""

    emitted = 0
    for analysis in analyses:
        for finding in analysis.result.findings:
            if emitted >= limit:
                return
            relative = analysis.file_path.relative_to(root)
            print(
                f"{relative}:{finding.line_number}-{finding.following_line_number}: "
                f"{finding.first_text.strip()} || "
                f"{finding.following_text.strip()}"
            )
            emitted += 1


def parse_args(arguments: list[str]) -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(add_help=False, description=__doc__)
    parser.add_argument("--help", action="help", help="Show this help message")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect",
    )
    parser.add_argument(
        "--mode",
        choices=("check", "count", "preview", "write"),
        default="check",
        help="Operation mode; check is the default",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_PREVIEW_LIMIT,
        help="Maximum preview findings to print",
    )
    parser.add_argument(
        "--immutable-manifest",
        type=Path,
        help="TOML with exact stage-history path and SHA-256 exceptions",
    )
    parsed = parser.parse_args(arguments)
    if parsed.limit < 0:
        parser.error("--limit must be non-negative")
    return parsed


def main(arguments: list[str]) -> int:
    """Run the requested repository Markdown normalization mode."""

    parsed = parse_args(arguments)
    root = parsed.root.expanduser().resolve(strict=True)
    try:
        exceptions = (
            load_immutable_manifest(root, parsed.immutable_manifest)
            if parsed.immutable_manifest is not None
            else ()
        )
        analyses = analyze_repository(root)
        validate_immutable_findings(root, analyses, exceptions)
        mutable = mutable_analyses(root, analyses, exceptions)
        print_summary(mutable)
        affected = [analysis for analysis in mutable if analysis.result.join_count > 0]
        if parsed.mode == "preview":
            print_preview(root, mutable, parsed.limit)
        elif parsed.mode == "write":
            for analysis in affected:
                write_text_atomic(
                    analysis.file_path,
                    analysis.source_text,
                    analysis.result.text,
                )
                print(f"normalized={analysis.file_path.relative_to(root)}")
            if parsed.immutable_manifest is not None:
                exceptions = load_immutable_manifest(root, parsed.immutable_manifest)
            post_write_analyses = analyze_repository(root)
            validate_immutable_findings(root, post_write_analyses, exceptions)
            remaining = [
                analysis
                for analysis in mutable_analyses(
                    root, post_write_analyses, exceptions
                )
                if analysis.result.join_count > 0
            ]
            if remaining:
                raise MarkdownNormalizationError(
                    "normalization left prose continuation breaks"
                )
        elif parsed.mode == "check" and affected:
            print(
                "Markdown prose hard-wrap detected; run preview before write.",
                file=sys.stderr,
            )
            print_preview(root, mutable, parsed.limit)
            return 1
    except (MarkdownNormalizationError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
