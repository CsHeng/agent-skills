#!/usr/bin/env python3
"""Check a repository documentation layout against its own declared manifest.

The manifest is the single source of placement truth: declared documentation
roots, their index and closure obligations, stage-bundle shape, archive class
shape, link-resolution scope, and named exceptions. This tool never infers a
root from prose and never depends on another repository checkout.

Capabilities:
  declared-roots        every documentation-bearing root is declared and indexed
  stage-shape           stage bundles follow the declared domain/topic shape
  archive-shape         the archive root holds only declared class subroots
  root-shape            per-root file naming rules
  index-closure         each declared index references every file it owns
  link-resolution       offline relative link resolution with scope classes
  migration-conservation relocation manifests keep path pairs and SHA-256 truth

Exit status is 1 when any finding is not covered by a declared exception.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, NoReturn, Sequence

SCHEMA = "organize-docs/documentation-layout@1"
DEFAULT_MANIFEST = "testing/documentation-layout.json"

CAPABILITIES = (
    "declared-roots",
    "stage-shape",
    "archive-shape",
    "root-shape",
    "index-closure",
    "link-resolution",
    "migration-conservation",
)

LINK_SCHEMES = re.compile(r"^[A-Za-z][A-Za-z0-9+.\-]*:")
INLINE_LINK = re.compile(r"!?\[[^\]]*\]\(\s*([^()\s]+)(?:\s+\"[^\"]*\")?\s*\)")
REFERENCE_LINK = re.compile(r"!?\[[^\]]*\]\[\s*([^\]]+?)\s*\]")
REFERENCE_DEF = re.compile(r"^\s{0,3}\[([^\]]+)\]:\s*(\S+)", re.MULTILINE)
HTML_TARGET = re.compile(r"(?:href|src)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
CODE_FENCE = re.compile(r"^\s*(```|~~~)")

SKIP_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    ".tox",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "dist",
    "build",
    ".dist",
    ".agents/worktrees",
    ".agents/tmp",
}


@dataclass(frozen=True)
class Finding:
    """One manifest violation with enough context to repair it."""

    check: str
    rule: str
    path: str
    message: str


@dataclass
class Report:
    """Gate results, split into violations and declared-exception exemptions."""

    findings: list[Finding] = field(default_factory=list)
    exempt: list[Finding] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def exempt_add(self, finding: Finding) -> None:
        self.exempt.append(finding)


class ManifestError(Exception):
    """The manifest itself is unusable."""


def fail(message: str) -> NoReturn:
    raise ManifestError(message)


def rel(root: Path, path: Path) -> str:
    """Render a path relative to the repository root for stable reporting."""

    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        fail(f"manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"manifest is not valid JSON: {path}: {exc}")
    if not isinstance(data, dict):
        fail(f"manifest root must be an object: {path}")
    if data.get("schema") != SCHEMA:
        fail(f"manifest schema must be {SCHEMA}: {path}")
    if not data.get("repository"):
        fail("manifest must declare repository")
    checks = data.get("checks")
    if not isinstance(checks, list) or not checks:
        fail("manifest must declare a non-empty checks list")
    for entry in checks:
        if not isinstance(entry, dict) or not entry.get("id"):
            fail("every check must declare an id")
        capabilities = entry.get("capabilities")
        if not isinstance(capabilities, list) or not capabilities:
            fail(f"check {entry['id']} must declare capabilities")
        for capability in capabilities:
            if capability not in CAPABILITIES:
                fail(f"check {entry['id']} declares unknown capability {capability}")
    roots = data.get("roots")
    if not isinstance(roots, list) or not roots:
        fail("manifest must declare a non-empty roots list")
    for entry in roots:
        if not isinstance(entry, dict) or not entry.get("path"):
            fail("every root must declare a path")
    return data


def tracked_files(root: Path) -> list[Path]:
    """Enumerate repository files that gates must read.

    A Git work tree yields tracked plus untracked-but-not-ignored paths, so
    ignored local evidence stays out of every gate while freshly authored
    indexes are still checked before they are staged. Non-Git fixture trees
    fall back to a directory walk that skips generated and VCS directories.
    """

    if (root / ".git").exists():
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            names = [item for item in result.stdout.split("\0") if item]
            paths = [root / name for name in names if (root / name).is_file()]
            return sorted(paths, key=lambda item: item.relative_to(root).as_posix())
    paths = []
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root)
        if any(part in SKIP_DIRECTORIES for part in relative.parts):
            continue
        paths.append(candidate)
    return sorted(paths, key=lambda item: item.relative_to(root).as_posix())


def documentation_extensions(manifest: dict[str, Any]) -> tuple[str, ...]:
    extensions = manifest.get("documentationExtensions") or [".md"]
    return tuple(str(item) for item in extensions)


def root_entries(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [entry for entry in manifest["roots"] if isinstance(entry, dict)]


def root_by_path(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(entry["path"]).rstrip("/"): entry for entry in root_entries(manifest)}


def classify_scope(
    manifest: dict[str, Any], relative: str
) -> tuple[str, dict[str, Any] | None]:
    """Return the link scope and owning declared root for a relative path."""

    best: dict[str, Any] | None = None
    best_length = -1
    for entry in root_entries(manifest):
        declared = str(entry["path"]).rstrip("/")
        if relative == declared or relative.startswith(declared + "/"):
            if len(declared) > best_length:
                best = entry
                best_length = len(declared)
    scope = str((best or {}).get("linkScope") or "current")
    return scope, best


def is_ignored_path(manifest: dict[str, Any], relative: str) -> bool:
    for entry in manifest.get("gateExclusions") or []:
        prefix = str(entry.get("path") or entry).rstrip("/")
        if relative == prefix or relative.startswith(prefix + "/"):
            return True
    return False


def exception_paths(manifest: dict[str, Any], key: str) -> list[dict[str, Any]]:
    entries = (manifest.get("exceptions") or {}).get(key) or []
    normalized: list[dict[str, Any]] = []
    for entry in entries:
        if isinstance(entry, str):
            normalized.append({"path": entry, "reason": "declared exception"})
        elif isinstance(entry, dict) and entry.get("path"):
            normalized.append(entry)
    return normalized


def matches_prefix(relative: str, prefix: str) -> bool:
    prefix = prefix.rstrip("/")
    return relative == prefix or relative.startswith(prefix + "/")


def declared_exception(
    manifest: dict[str, Any], key: str, relative: str
) -> dict[str, Any] | None:
    for entry in exception_paths(manifest, key):
        if matches_prefix(relative, str(entry["path"])):
            return entry
    return None


# --------------------------------------------------------------------------
# Markdown link extraction
# --------------------------------------------------------------------------


def strip_code_fences(text: str) -> str:
    """Remove fenced code blocks so examples are not read as links."""

    kept: list[str] = []
    fenced = False
    for line in text.splitlines():
        if CODE_FENCE.match(line):
            fenced = not fenced
            continue
        if not fenced:
            kept.append(line)
    return "\n".join(kept)


def frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    parts = text.split("\n")
    for index in range(1, len(parts)):
        if parts[index].strip() in ("---", "..."):
            return "\n".join(parts[1:index]), "\n".join(parts[index + 1 :])
    return "", text


def extract_links(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    _, body = frontmatter(text)
    body = strip_code_fences(body)
    targets: list[str] = []
    targets.extend(INLINE_LINK.findall(body))
    targets.extend(HTML_TARGET.findall(body))
    definitions = dict(REFERENCE_DEF.findall(body))
    for label in REFERENCE_LINK.findall(body):
        resolved = definitions.get(label)
        if resolved:
            targets.append(resolved)
    return targets


def is_external(target: str) -> bool:
    stripped = target.strip()
    if not stripped:
        return True
    if stripped.startswith(("#", "//", "mailto:")):
        return True
    if LINK_SCHEMES.match(stripped):
        return True
    if any(char in stripped for char in ("{{", "}}", "<", ">", "*", "${")):
        return True
    return False


def normalize_target(target: str) -> str:
    stripped = target.strip()
    stripped = stripped.split("#", 1)[0]
    stripped = stripped.split("?", 1)[0]
    if stripped.endswith("/"):
        stripped = stripped[:-1]
    return stripped


# --------------------------------------------------------------------------
# Capabilities
# --------------------------------------------------------------------------


def check_declared_roots(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    declared = root_by_path(manifest)
    extensions = documentation_extensions(manifest)

    for required in manifest.get("requiredFiles") or []:
        if not (root / str(required)).is_file():
            report.add(
                Finding(
                    check_id,
                    "required-file-missing",
                    str(required),
                    "manifest requires this documentation file and it does not exist",
                )
            )

    declared_classes = {
        str(item["name"]): str(item.get("meaning") or "")
        for item in manifest.get("classes") or []
        if isinstance(item, dict) and item.get("name")
    }
    for path, entry in sorted(declared.items()):
        material_class = str(entry.get("class") or "")
        if declared_classes and material_class not in declared_classes:
            report.add(
                Finding(
                    check_id,
                    "undeclared-material-class",
                    path,
                    f"material class '{material_class}' is not in the declared class vocabulary {sorted(declared_classes)}",
                )
            )
        absolute = root / path
        if not (absolute.is_dir() or absolute.is_file()):
            report.add(
                Finding(check_id, "declared-root-missing", path, "declared root does not exist")
            )
            continue
        if absolute.is_file():
            continue
        index = entry.get("index")
        if index and not (absolute / str(index)).is_file():
            report.add(
                Finding(
                    check_id,
                    "declared-index-missing",
                    f"{path}/{index}",
                    "declared root index does not exist",
                )
            )

    # Every documentation-bearing directory must be declared or excepted.
    declared_prefixes = sorted(declared, key=len, reverse=True)
    scanned = [str(item) for item in manifest.get("scannedRoots") or []]
    if not scanned:
        scanned = ["."]
    seen: set[str] = set()
    for scan in scanned:
        scan_root = root / scan
        if not scan_root.is_dir():
            continue
        depth_limit = int(manifest.get("undeclaredRootDepth") or 3)
        base_depth = len(scan_root.relative_to(root).parts) if scan != "." else 0
        for candidate in sorted(scan_root.rglob("*")):
            if not candidate.is_dir():
                continue
            relative = candidate.relative_to(root).as_posix()
            if any(part in SKIP_DIRECTORIES for part in candidate.relative_to(root).parts):
                continue
            if is_ignored_path(manifest, relative):
                continue
            if len(candidate.relative_to(root).parts) - base_depth > depth_limit:
                continue
            owner = next(
                (prefix for prefix in declared_prefixes if matches_prefix(relative, prefix)),
                None,
            )
            if owner is not None and not declared[owner].get("containerRoot"):
                continue
            if owner is not None and relative == owner:
                continue
            if declared_exception(manifest, "undeclaredDocumentationRoots", relative):
                continue
            has_docs = any(
                item.is_file() and item.suffix in extensions
                for item in candidate.iterdir()
            )
            if not has_docs:
                continue
            if relative in seen:
                continue
            seen.add(relative)
            report.add(
                Finding(
                    check_id,
                    "undeclared-documentation-root",
                    relative,
                    "directory holds documentation files but is not a declared root",
                )
            )


def _stage_config(manifest: dict[str, Any]) -> dict[str, Any]:
    stage = manifest.get("stage")
    if not isinstance(stage, dict):
        fail("stage-shape capability requires a stage object in the manifest")
    return stage


def check_stage_shape(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    """Verify the stage root holds only declared domains and well-formed bundles."""

    stage = _stage_config(manifest)
    stage_root = str(stage["root"]).rstrip("/")
    absolute = root / stage_root
    if not absolute.is_dir():
        report.add(
            Finding(check_id, "stage-root-missing", stage_root, "declared stage root does not exist")
        )
        return

    domains = [str(item) for item in stage.get("domains") or []]
    require_domain_segment = bool(stage.get("domainSegment", True))
    bundle_parent = str(stage.get("bundleParent") or "changes")
    plan_file = str(stage.get("planFile") or "plan.md")
    plan_pattern = stage.get("planPattern")
    records_dir = str(stage.get("recordsDir") or "records")
    record_extensions = tuple(str(item) for item in stage.get("recordExtensions") or [".json"])
    bundle_name_pattern = stage.get("bundleDirPattern")
    optional_members = {str(item) for item in stage.get("optionalMembers") or []}
    flat_exceptions = {str(item) for item in stage.get("flatFileExceptions") or ["README.md"]}
    plan_compiled = re.compile(plan_pattern) if plan_pattern else None
    bundle_compiled = re.compile(bundle_name_pattern) if bundle_name_pattern else None

    stage_report: dict[str, int] = report.counts.setdefault("stage", {})  # type: ignore[assignment]
    stage_report.update({"bundles": 0, "records": 0, "domains": len(domains)})

    if require_domain_segment:
        for entry in sorted(absolute.iterdir()):
            if entry.is_file():
                if entry.name in flat_exceptions:
                    continue
                report.add(
                    Finding(
                        check_id,
                        "stage-flat-file",
                        rel(root, entry),
                        f"stage root holds a loose file outside a bundle; allowed: {sorted(flat_exceptions)}",
                    )
                )
                continue
            if entry.name not in domains:
                report.add(
                    Finding(
                        check_id,
                        "stage-undeclared-domain",
                        rel(root, entry),
                        f"stage segment is not a declared domain; declared: {domains}",
                    )
                )
                continue
            for child in sorted(entry.iterdir()):
                if child.is_file():
                    if child.name != "README.md":
                        report.add(
                            Finding(
                                check_id,
                                "stage-domain-loose-file",
                                rel(root, child),
                                "domain directory holds a file other than its index",
                            )
                        )
                    continue
                if child.name != bundle_parent:
                    report.add(
                        Finding(
                            check_id,
                            "stage-domain-subroot",
                            rel(root, child),
                            f"domain directory holds a subroot other than {bundle_parent}/",
                        )
                    )
                    continue
                for item in sorted(child.iterdir()):
                    if item.is_file():
                        report.add(
                            Finding(
                                check_id,
                                "stage-bundle-parent-file",
                                rel(root, item),
                                f"file sits directly under {bundle_parent}/ instead of inside a bundle",
                            )
                        )
                        continue
                    _check_bundle(
                        root,
                        manifest,
                        report,
                        check_id,
                        item,
                        plan_file,
                        plan_compiled,
                        bundle_compiled,
                        records_dir,
                        record_extensions,
                        optional_members,
                        stage_report,
                    )
        for domain in domains:
            index = absolute / domain / "README.md"
            if not index.is_file():
                report.add(
                    Finding(
                        check_id,
                        "stage-domain-index-missing",
                        rel(root, index),
                        "declared domain has no index",
                    )
                )
        return

    parent = absolute / bundle_parent
    if not parent.is_dir():
        report.add(
            Finding(check_id, "stage-bundle-parent-missing", rel(root, parent), "declared bundle parent does not exist")
        )
        return
    for item in sorted(parent.iterdir()):
        if item.is_file():
            report.add(
                Finding(
                    check_id,
                    "stage-bundle-parent-file",
                    rel(root, item),
                    f"file sits directly under {bundle_parent}/ instead of inside a bundle",
                )
            )
            continue
        _check_bundle(
            root,
            manifest,
            report,
            check_id,
            item,
            plan_file,
            plan_compiled,
            bundle_compiled,
            records_dir,
            record_extensions,
            optional_members,
            stage_report,
        )


def _check_bundle(
    root: Path,
    manifest: dict[str, Any],
    report: Report,
    check_id: str,
    bundle: Path,
    plan_file: str,
    plan_compiled: re.Pattern[str] | None,
    bundle_compiled: re.Pattern[str] | None,
    records_dir: str,
    record_extensions: tuple[str, ...],
    optional_members: set[str],
    stage_report: dict[str, int],
) -> None:
    """Check one bundle directory's name, plan, record placement and members."""

    bundle_relative = rel(root, bundle)
    if bundle_compiled and not bundle_compiled.match(bundle.name):
        report.add(
            Finding(
                check_id,
                "stage-bundle-name",
                bundle_relative,
                f"bundle directory does not match {bundle_compiled.pattern}",
            )
        )
    members = [item for item in sorted(bundle.rglob("*")) if item.is_file()]
    top_level = [item for item in members if item.parent == bundle]
    has_plan = any(item.name == plan_file for item in top_level) or any(
        plan_compiled is not None and plan_compiled.match(item.name) for item in top_level
    )
    if not has_plan:
        report.add(
            Finding(
                check_id,
                "stage-bundle-plan-missing",
                bundle_relative,
                f"bundle has no {plan_file} or <repository>-plan.md",
            )
        )
    for item in members:
        inside = item.relative_to(bundle).as_posix()
        if item.suffix in record_extensions:
            stage_report["records"] = stage_report.get("records", 0) + 1
            if not inside.startswith(records_dir + "/"):
                report.add(
                    Finding(
                        check_id,
                        "stage-record-placement",
                        rel(root, item),
                        f"machine record must live under {records_dir}/",
                    )
                )
            continue
        if item.parent != bundle:
            report.add(
                Finding(
                    check_id,
                    "stage-nested-prose",
                    rel(root, item),
                    f"non-record file must sit at the bundle top level, not under {item.parent.name}/",
                )
            )
            continue
        if item.name == plan_file:
            continue
        if plan_compiled is not None and plan_compiled.match(item.name):
            continue
        if inside in optional_members:
            continue
        report.add(
            Finding(
                check_id,
                "stage-undeclared-member",
                rel(root, item),
                "bundle member is not a plan, a record, or a declared optional member",
            )
        )
    stage_report["bundles"] = stage_report.get("bundles", 0) + 1
def check_archive_shape(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    archive = manifest.get("archive")
    if not isinstance(archive, dict):
        fail("archive-shape capability requires an archive object in the manifest")
    archive_root = str(archive["root"]).rstrip("/")
    absolute = root / archive_root
    if not absolute.is_dir():
        report.add(Finding(check_id, "archive-root-missing", archive_root, "declared archive root does not exist"))
        return
    allowed_files = {str(item) for item in archive.get("allowRootFiles") or ["README.md"]}
    class_subroots = [str(item) for item in archive.get("classSubroots") or []]
    naming_exceptions = {
        str(item["path"]).rstrip("/"): str(item.get("reason") or "")
        for item in archive.get("namingExceptions") or []
        if isinstance(item, dict) and item.get("path")
    }
    for item in sorted(absolute.iterdir()):
        relative = item.relative_to(root).as_posix()
        if item.is_file():
            if item.name in allowed_files:
                continue
            report.add(
                Finding(
                    check_id,
                    "archive-loose-file",
                    relative,
                    "archive root holds a loose file instead of a class subroot",
                )
            )
            continue
        name = item.name
        if class_subroots and name not in class_subroots and name not in naming_exceptions:
            report.add(
                Finding(
                    check_id,
                    "archive-undeclared-class",
                    relative,
                    f"archive subroot is not a declared class subroot; declared: {class_subroots}",
                )
            )
        index = item / "README.md"
        if not index.is_file():
            report.add(
                Finding(
                    check_id,
                    "archive-class-index-missing",
                    rel(root, index),
                    "archive class subroot has no index",
                )
            )
    for name in naming_exceptions:
        if not (root / name).exists():
            report.add(
                Finding(
                    check_id,
                    "archive-naming-exception-stale",
                    name,
                    "declared archive naming exception no longer matches a path",
                )
            )


def check_root_shape(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    for entry in root_entries(manifest):
        pattern = entry.get("filePattern")
        if not pattern:
            continue
        declared = str(entry["path"]).rstrip("/")
        absolute = root / declared
        if not absolute.is_dir():
            continue
        compiled = re.compile(pattern)
        allowed = {str(item) for item in entry.get("filePatternAllow") or []}
        extensions = tuple(str(item) for item in entry.get("extensions") or documentation_extensions(manifest))
        for item in sorted(absolute.iterdir()):
            if not item.is_file() or item.suffix not in extensions:
                continue
            relative = item.relative_to(root).as_posix()
            if relative in allowed or item.name in allowed:
                continue
            if not compiled.match(item.name):
                report.add(
                    Finding(
                        check_id,
                        "root-file-pattern",
                        relative,
                        f"file does not match the declared pattern {pattern}",
                    )
                )


def check_index_closure(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    """Require declared indexes to exist and to reference every file they own."""

    for entry in root_entries(manifest):
        declared = str(entry["path"]).rstrip("/")
        absolute = root / declared
        if not absolute.is_dir():
            continue
        _check_subdirectory_indexes(root, manifest, report, check_id, entry, absolute)
        if not entry.get("closure"):
            continue
        extensions = tuple(
            str(item) for item in entry.get("extensions") or documentation_extensions(manifest)
        )
        record_extensions = tuple(str(item) for item in entry.get("recordExtensions") or [".json"])
        owned_extensions = extensions + record_extensions + tuple(
            str(item) for item in entry.get("ownedExtensions") or [".puml", ".svg", ".yaml"]
        )
        index_names = {str(entry.get("index") or "README.md")}
        index_names.update(str(item) for item in entry.get("closureIndexes") or [])
        index_patterns = [
            re.compile(str(item)) for item in entry.get("closureIndexPatterns") or []
        ]

        def is_index(path: Path) -> bool:
            if path.name in index_names:
                return True
            return any(pattern.match(path.name) for pattern in index_patterns)

        referenced: set[str] = set()
        owned: list[str] = []
        for item in sorted(absolute.rglob("*")):
            relative = item.relative_to(root).as_posix()
            if is_ignored_path(manifest, relative):
                continue
            if item.is_dir():
                continue
            if is_index(item):
                for target in extract_links(item):
                    if is_external(target):
                        continue
                    normalized = normalize_target(target)
                    if not normalized:
                        continue
                    base = Path() if normalized.startswith("/") else item.parent.relative_to(root)
                    try:
                        resolved = _resolve_lexical(root, base / normalized.lstrip("/"))
                    except _OutsideRoot:
                        continue
                    referenced.add(resolved.as_posix())
                continue
            if item.suffix not in owned_extensions:
                continue
            owned.append(relative)

        unreferenced = 0
        for relative in owned:
            if relative in referenced:
                continue
            if declared_exception(manifest, "closureExempt", relative):
                report.exempt_add(
                    Finding(check_id, "index-closure-exempt", relative, "declared closure exception")
                )
                continue
            unreferenced += 1
            report.add(
                Finding(
                    check_id,
                    "index-closure",
                    relative,
                    f"no index inside {declared} references this file",
                )
            )
        report.counts[f"closureOwned:{declared}"] = len(owned)
        report.counts[f"closureUnreferenced:{declared}"] = unreferenced


def _migration_manifest_names(manifest: dict[str, Any]) -> set[str]:
    stage = manifest.get("stage") or {}
    names = {str(item) for item in manifest.get("migrationManifestNames") or []}
    legacy = stage.get("migrationManifest")
    if legacy:
        names.add(str(legacy).split("/")[-1])
    if not names:
        names.add("migration-manifest.json")
    return names


def _migration_manifest_files(root: Path, manifest: dict[str, Any], absolute: Path) -> list[Path]:
    names = _migration_manifest_names(manifest)
    found: list[Path] = []
    for name in sorted(names):
        for candidate in sorted(absolute.rglob(name)):
            relative = candidate.relative_to(root).as_posix()
            if candidate.is_file() and not is_ignored_path(manifest, relative):
                found.append(candidate)
    return sorted(set(found), key=lambda item: item.relative_to(root).as_posix())


def _check_subdirectory_indexes(
    root: Path,
    manifest: dict[str, Any],
    report: Report,
    check_id: str,
    entry: dict[str, Any],
    absolute: Path,
) -> None:
    """Require an index in every documentation-bearing subdirectory up to a depth."""

    rule = entry.get("subdirectoryIndexes")
    if not isinstance(rule, dict):
        return
    max_depth = int(rule.get("maxDepth") or 1)
    index_name = str(rule.get("index") or "README.md")
    declared = str(entry["path"]).rstrip("/")
    extensions = tuple(
        str(item) for item in entry.get("extensions") or documentation_extensions(manifest)
    )
    missing = 0
    for directory in sorted(absolute.rglob("*")):
        if not directory.is_dir():
            continue
        relative = directory.relative_to(root).as_posix()
        if is_ignored_path(manifest, relative):
            continue
        depth = len(directory.relative_to(absolute).parts)
        if depth > max_depth:
            continue
        if declared_exception(manifest, "subdirectoryIndexExempt", relative):
            report.exempt_add(
                Finding(check_id, "namespace-index-exempt", relative, "declared namespace index exception")
            )
            continue
        holds_documentation = any(
            item.is_file() and item.suffix in extensions and not is_ignored_path(manifest, item.relative_to(root).as_posix())
            for item in directory.iterdir()
        )
        if not holds_documentation:
            continue
        if (directory / index_name).is_file():
            continue
        missing += 1
        report.add(
            Finding(
                check_id,
                "namespace-index-missing",
                f"{relative}/{index_name}",
                f"documentation namespace inside {declared} has no index",
            )
        )
    report.counts[f"namespaceIndexesMissing:{declared}"] = missing


class _OutsideRoot(Exception):
    pass


def _resolve_lexical(root: Path, candidate: Path) -> Path:
    """Resolve without touching the filesystem, raising when it escapes root."""

    parts: list[str] = []
    anchored = candidate.is_absolute()
    for part in candidate.parts:
        if part == "/":
            continue
        if part == ".":
            continue
        if part == "..":
            if not parts:
                raise _OutsideRoot
            parts.pop()
            continue
        parts.append(part)
    resolved = Path(*parts) if parts else Path(".")
    if anchored:
        resolved = Path("/") / resolved
    return resolved


def declared_archived_pointer(
    manifest: dict[str, Any], relative: str, resolved: str
) -> dict[str, Any] | None:
    entries = (manifest.get("archive") or {}).get("unresolvedPointers") or []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if str(entry.get("from")) == relative and str(entry.get("to")) == resolved:
            return entry
    return None


def check_frontmatter_links(
    root: Path, path: Path, owner: dict[str, Any], report: Report, check_id: str
) -> None:
    """Resolve declared scalar path fields, without staged prose exemptions."""

    fields = owner.get("frontmatterLinkFields") or []
    if not fields:
        return
    header, _ = frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    for name in fields:
        match = re.search(rf"^{re.escape(str(name))}:[ \t]*(.*)$", header, re.MULTILINE)
        if match is None:
            continue
        value = match.group(1).strip()
        scalar = re.fullmatch(r'''(?:"([^"]*)"|'([^']*)'|([^#'"\s][^#]*?))(?:\s+#.*)?''', value)
        target = next((part for part in scalar.groups() if part is not None), "").strip() if scalar else ""
        try:
            if not target or is_external(target) or target.startswith("/"):
                raise _OutsideRoot
            resolved = _resolve_lexical(root, path.parent.relative_to(root) / normalize_target(target))
            valid = (root / resolved).is_file()
        except _OutsideRoot:
            valid = False
        if not valid:
            report.add(Finding(
                check_id, "frontmatter-link-unresolved", rel(root, path),
                f"{name} must name an existing repository-local file relative to this document: {value}",
            ))


def check_link_resolution(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    extensions = documentation_extensions(manifest)
    archived_basis = {
        str(item.get("path", "")).rstrip("/"): str(item.get("reason") or "archived scope")
        for item in (manifest.get("archive") or {}).get("linkExceptions") or []
        if isinstance(item, dict)
    }
    staged_basis = str((manifest.get("stage") or {}).get("linkExceptionBasis") or "staged scope")
    scopes = {"current": 0, "archived": 0, "staged": 0, "excluded": 0}
    unresolved_current = 0
    for path in tracked_files(root):
        relative = path.relative_to(root).as_posix()
        if path.suffix not in extensions:
            continue
        if is_ignored_path(manifest, relative):
            continue
        scope, owner = classify_scope(manifest, relative)
        if scope == "excluded":
            scopes["excluded"] += 1
            continue
        scopes[scope] = scopes.get(scope, 0) + 1
        check_frontmatter_links(root, path, owner or {}, report, check_id)
        owner_path = str((owner or {}).get("path", "")).rstrip("/")
        exempt_scope = scope in ("archived", "staged")
        basis = archived_basis.get(owner_path, "archived scope") if scope == "archived" else staged_basis
        for raw in extract_links(path):
            if is_external(raw):
                continue
            normalized = normalize_target(raw)
            if not normalized:
                continue
            base = Path() if normalized.startswith("/") else path.parent.relative_to(root)
            candidate = base / normalized.lstrip("/")
            try:
                resolved = _resolve_lexical(root, candidate)
            except _OutsideRoot:
                target_label = normalized
                entry = declared_exception(manifest, "declaredPins", relative)
                if exempt_scope:
                    report.exempt_add(
                        Finding(
                            check_id,
                            f"link-escapes-root-{scope}",
                            f"{relative} -> {target_label}",
                            basis,
                        )
                    )
                elif entry:
                    report.exempt_add(
                        Finding(
                            check_id,
                            "link-escapes-root-declared",
                            f"{relative} -> {target_label}",
                            str(entry.get("reason") or "declared pin"),
                        )
                    )
                else:
                    unresolved_current += 1
                    report.add(
                        Finding(
                            check_id,
                            "link-escapes-root",
                            f"{relative} -> {target_label}",
                            "link resolves outside this repository and is not a declared pin",
                        )
                    )
                continue
            resolved_relative = resolved.as_posix()
            absolute = root / resolved
            if absolute.exists():
                if absolute.is_dir() and not (absolute / "README.md").is_file() and not (absolute / "index.md").is_file():
                    if exempt_scope:
                        report.exempt_add(
                            Finding(check_id, f"link-directory-index-{scope}", f"{relative} -> {resolved_relative}", basis)
                        )
                    else:
                        unresolved_current += 1
                        report.add(
                            Finding(
                                check_id,
                                "link-directory-index",
                                f"{relative} -> {resolved_relative}",
                                "link targets a directory with no index",
                            )
                        )
                continue
            entry = declared_exception(manifest, "unresolvableLinks", relative)
            if entry and matches_prefix(f"{relative} -> {resolved_relative}", str(entry["path"])):
                report.exempt_add(
                    Finding(check_id, "link-unresolved-declared", f"{relative} -> {resolved_relative}", str(entry.get("reason")))
                )
                continue
            if scope == "archived":
                declared = declared_archived_pointer(manifest, relative, resolved_relative)
                if declared is None:
                    report.add(
                        Finding(
                            check_id,
                            "link-unresolved-archived-undeclared",
                            f"{relative} -> {resolved_relative}",
                            "archived pointer stays unresolved but is not declared in the manifest's archived exception list",
                        )
                    )
                else:
                    report.exempt_add(
                        Finding(
                            check_id,
                            "link-unresolved-archived",
                            f"{relative} -> {resolved_relative}",
                            str(declared.get("reason") or basis),
                        )
                    )
                continue
            if exempt_scope:
                report.exempt_add(
                    Finding(
                        check_id,
                        f"link-unresolved-{scope}",
                        f"{relative} -> {resolved_relative}",
                        basis,
                    )
                )
                continue
            unresolved_current += 1
            report.add(
                Finding(
                    check_id,
                    "link-unresolved",
                    f"{relative} -> {resolved_relative}",
                    "relative link target does not exist in the current scope",
                )
            )
    report.counts["links"] = sum(scopes.values())
    report.counts["linksCurrentScope"] = scopes.get("current", 0)
    report.counts["linksArchivedScope"] = scopes.get("archived", 0)
    report.counts["linksStagedScope"] = scopes.get("staged", 0)
    report.counts["linksExcludedScope"] = scopes.get("excluded", 0)
    report.counts["unresolvedCurrent"] = unresolved_current


def check_migration_conservation(
    root: Path, manifest: dict[str, Any], report: Report, check_id: str
) -> None:
    stage = manifest.get("stage") or {}
    names = _migration_manifest_names(manifest)
    required = bool(stage.get("requireMigrationManifest", False))
    search_roots = [root / str(item) for item in manifest.get("migrationManifestRoots") or []] or [root]
    manifests: list[Path] = []
    for search in search_roots:
        if not search.is_dir():
            continue
        manifests.extend(_migration_manifest_files(root, manifest, search))
    if required and not manifests:
        report.add(
            Finding(
                check_id,
                "migration-manifest-missing",
                rel(root, search_roots[0]),
                f"manifest requires migration manifests named {sorted(names)} but none exist",
            )
        )
    seen_pairs = 0
    for manifest_path in manifests:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            report.add(Finding(check_id, "migration-manifest-invalid", rel(root, manifest_path), str(exc)))
            continue
        moves = data.get("moved")
        if not isinstance(moves, list) or not moves:
            report.add(
                Finding(check_id, "migration-manifest-empty", rel(root, manifest_path), "manifest declares no moved entries")
            )
            continue
        for move in moves:
            if not isinstance(move, dict):
                report.add(Finding(check_id, "migration-entry-invalid", rel(root, manifest_path), "moved entry is not an object"))
                continue
            source = str(move.get("from") or "")
            destination = str(move.get("to") or "")
            if not source or not destination:
                report.add(
                    Finding(check_id, "migration-entry-incomplete", rel(root, manifest_path), f"entry lacks from/to: {move}")
                )
                continue
            seen_pairs += 1
            destination_path = root / destination
            if not destination_path.is_file():
                report.add(
                    Finding(check_id, "migration-destination-missing", destination, "declared new path does not exist")
                )
                continue
            expected = str(move.get("sha256") or "")
            if expected:
                actual = hashlib.sha256(destination_path.read_bytes()).hexdigest()
                if actual != expected:
                    report.add(
                        Finding(
                            check_id,
                            "migration-hash-mismatch",
                            destination,
                            f"declared sha256 {expected[:12]} does not match current {actual[:12]}",
                        )
                    )
            source_path = root / source
            if source_path.exists():
                report.add(
                    Finding(check_id, "migration-source-survives", source, "declared old path still exists beside its new path")
                )
        for created in data.get("created") or []:
            if not isinstance(created, dict) or not created.get("path"):
                report.add(
                    Finding(check_id, "migration-created-invalid", rel(root, manifest_path), f"created entry is not an object: {created}")
                )
                continue
            created_path = root / str(created["path"])
            if not created_path.is_file():
                report.add(
                    Finding(check_id, "migration-created-missing", str(created["path"]), "declared created path does not exist")
                )
                continue
            expected = str(created.get("sha256") or "")
            if expected:
                actual = hashlib.sha256(created_path.read_bytes()).hexdigest()
                if actual != expected:
                    report.add(
                        Finding(
                            check_id,
                            "migration-created-hash-mismatch",
                            str(created["path"]),
                            f"declared sha256 {expected[:12]} does not match current {actual[:12]}",
                        )
                    )
        for repair in data.get("pointerRepairs") or []:
            if not isinstance(repair, dict) or not repair.get("path"):
                report.add(
                    Finding(check_id, "migration-repair-invalid", rel(root, manifest_path), f"pointer repair is not an object: {repair}")
                )
    report.counts["migrationManifests"] = len(manifests)
    report.counts["migrationPairs"] = seen_pairs


CAPABILITY_HANDLERS = {
    "declared-roots": check_declared_roots,
    "stage-shape": check_stage_shape,
    "archive-shape": check_archive_shape,
    "root-shape": check_root_shape,
    "index-closure": check_index_closure,
    "link-resolution": check_link_resolution,
    "migration-conservation": check_migration_conservation,
}


def run_checks(root: Path, manifest: dict[str, Any]) -> Report:
    report = Report()
    for entry in manifest["checks"]:
        check_id = str(entry["id"])
        for capability in entry["capabilities"]:
            CAPABILITY_HANDLERS[capability](root, manifest, report, check_id)
    return report


def render(report: Report, limit: int, as_json: bool) -> str:
    if as_json:
        return json.dumps(
            {
                "findings": [item.__dict__ for item in report.findings],
                "exempt": [item.__dict__ for item in report.exempt],
                "counts": report.counts,
            },
            indent=2,
            sort_keys=True,
        )
    lines: list[str] = []
    grouped: dict[str, list[Finding]] = {}
    for finding in report.findings:
        grouped.setdefault(finding.check, []).append(finding)
    exempt_grouped: dict[str, dict[str, int]] = {}
    for finding in report.exempt:
        bucket = exempt_grouped.setdefault(finding.check, {})
        bucket[finding.rule] = bucket.get(finding.rule, 0) + 1
    for check_id in sorted(grouped):
        items = grouped[check_id]
        lines.append(f"{check_id}: {len(items)} violation(s)")
        for finding in items[:limit]:
            lines.append(f"  [{finding.rule}] {finding.path}: {finding.message}")
        if len(items) > limit:
            lines.append(f"  ... {len(items) - limit} more")
    for check_id in sorted(exempt_grouped):
        summary = ", ".join(f"{rule}={count}" for rule, count in sorted(exempt_grouped[check_id].items()))
        lines.append(f"{check_id}: declared exceptions: {summary}")
    for key in sorted(report.counts):
        value = report.counts[key]
        if isinstance(value, dict):
            rendered = ", ".join(f"{name}={value[name]}" for name in sorted(value))
            lines.append(f"count {key}: {rendered}")
        else:
            lines.append(f"count {key}: {value}")
    if not report.findings:
        lines.append("documentation layout: pass")
    return "\n".join(lines)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root to inspect")
    parser.add_argument("--manifest", type=Path, default=None, help=f"layout manifest path (default {DEFAULT_MANIFEST})")
    parser.add_argument("--limit", type=int, default=40, help="maximum findings printed per check")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable report")
    parser.add_argument("--check", action="append", default=[], help="restrict to a declared check id (repeatable)")
    return parser.parse_args(list(argv))


def main(argv: Sequence[str]) -> int:
    arguments = parse_args(argv)
    root = arguments.root.resolve()
    if not (root / ".git").exists() and not (root / "README.md").exists():
        print(f"ERROR: {root} does not look like a repository root", file=sys.stderr)
        return 2
    manifest_path = arguments.manifest or root / DEFAULT_MANIFEST
    if not manifest_path.is_absolute():
        manifest_path = root / manifest_path
    try:
        manifest = load_manifest(manifest_path)
    except ManifestError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    selected = set(arguments.check)
    if selected:
        manifest = dict(manifest)
        manifest["checks"] = [entry for entry in manifest["checks"] if str(entry["id"]) in selected]
        if not manifest["checks"]:
            print(f"ERROR: no declared check matches {sorted(selected)}", file=sys.stderr)
            return 2
    if arguments.limit < 0:
        print("ERROR: --limit must be non-negative", file=sys.stderr)
        return 2
    report = run_checks(root, manifest)
    print(render(report, arguments.limit, arguments.json))
    return 1 if report.findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
