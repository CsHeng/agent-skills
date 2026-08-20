#!/usr/bin/env python3
"""Shared root-flat skill generation and parity primitives."""

from __future__ import annotations

import json
import shutil
import stat
import sys
import tempfile
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.skill_activation import (  # noqa: E402
    derived_implicit_invocation,
    project_openai_metadata,
)
from src.runtime.harness.lifecycle import normalize_lifecycle_sources  # noqa: E402

RUNTIME_OWNERS = {
    "close-change",
    "design-change",
    "implement-change",
    "plan-change",
    "review-change",
    "sync-truth",
}


class DistributionError(RuntimeError):
    """Raised when authored or generated skill distribution is invalid."""


def replace_directory(
    staged: Path,
    destination: Path,
    promote: Callable[[Path, Path], None] | None = None,
) -> None:
    """Atomically replace a tree and restore its predecessor on promotion failure."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix=f".{destination.name}.old.", dir=destination.parent))
    backup.rmdir()
    had_destination = destination.exists()
    if had_destination:
        destination.rename(backup)
    promote_tree = promote or (lambda source, target: source.rename(target))
    try:
        promote_tree(staged, destination)
    except BaseException:
        if destination.exists():
            shutil.rmtree(destination)
        if had_destination and backup.exists():
            backup.rename(destination)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup)


def load_toml(path: Path) -> dict[str, Any]:
    """Load one TOML mapping."""
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_contract(repo_root: Path) -> dict[str, Any]:
    """Load and minimally validate the skill contract."""
    contract = load_toml(repo_root / "contracts" / "skills.toml")
    skills = contract.get("skills")
    if not isinstance(skills, dict) or len(skills) != 39:
        raise DistributionError("contracts/skills.toml must define exactly 39 skills")
    return contract


def load_bundles(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Load explicit production runtime bundle manifests."""
    bundles = load_toml(repo_root / "contracts" / "runtime-bundles.toml").get("bundles")
    if not isinstance(bundles, dict):
        raise DistributionError("runtime bundle contract must contain [bundles.*]")
    return bundles


def expected_runtime_owners(contract: dict[str, Any]) -> set[str]:
    """Return the exact contract-declared harness owner set."""
    skills = contract["skills"]
    owners = {
        skill_id
        for skill_id, entry in skills.items()
        if isinstance(entry, dict) and entry.get("runtime_bundle") == "harness"
    }
    if owners != RUNTIME_OWNERS:
        raise DistributionError(
            f"harness owners differ; expected={sorted(RUNTIME_OWNERS)} actual={sorted(owners)}"
        )
    return owners


def bundle_files(repo_root: Path, bundle_name: str) -> tuple[Path, str, dict[str, Path]]:
    """Resolve one explicit production bundle file set."""
    entry = load_bundles(repo_root).get(bundle_name)
    if not isinstance(entry, dict):
        raise DistributionError(f"unknown runtime bundle: {bundle_name}")
    source_value = entry.get("source")
    destination = entry.get("destination")
    files = entry.get("files")
    if not isinstance(source_value, str) or not isinstance(destination, str):
        raise DistributionError(f"invalid runtime bundle paths: {bundle_name}")
    if not isinstance(files, list) or not files or not all(isinstance(item, str) for item in files):
        raise DistributionError(f"invalid runtime bundle file manifest: {bundle_name}")
    if len(files) != len(set(files)):
        raise DistributionError(f"duplicate runtime bundle files: {bundle_name}")
    source = repo_root / source_value
    resolved: dict[str, Path] = {}
    for relative in files:
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise DistributionError(f"unsafe runtime bundle file: {relative}")
        source_file = source / relative_path
        if not source_file.is_file() or source_file.is_symlink():
            raise DistributionError(f"missing or symlinked runtime bundle file: {source_file}")
        resolved[relative_path.as_posix()] = source_file
    return source, destination, resolved


def _safe_bundle_relative(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise DistributionError(f"invalid runtime bundle {field}")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise DistributionError(f"unsafe runtime bundle {field}: {value}")
    return relative.as_posix()


def bundle_payloads(
    repo_root: Path, bundle_name: str
) -> tuple[Path, str, dict[str, bytes]]:
    """Render static files and canonical contract projections for one bundle."""
    source, destination, files = bundle_files(repo_root, bundle_name)
    payloads = {relative: path.read_bytes() for relative, path in files.items()}
    entry = load_bundles(repo_root)[bundle_name]
    projections = entry.get("projections", [])
    if not isinstance(projections, list):
        raise DistributionError(f"invalid runtime bundle projections: {bundle_name}")
    for projection in projections:
        if not isinstance(projection, dict):
            raise DistributionError(f"invalid runtime bundle projection: {bundle_name}")
        if projection.get("kind") != "lifecycle-contracts-v1":
            raise DistributionError(f"unknown runtime bundle projection: {bundle_name}")
        output = _safe_bundle_relative(projection.get("destination"), "projection destination")
        sources = projection.get("sources")
        if (
            not isinstance(sources, list)
            or len(sources) != 3
            or not all(isinstance(item, str) for item in sources)
        ):
            raise DistributionError(
                f"lifecycle projection requires exactly three sources: {bundle_name}"
            )
        source_paths: list[Path] = []
        for value in sources:
            relative = _safe_bundle_relative(value, "projection source")
            path = repo_root / relative
            if not path.is_file() or path.is_symlink():
                raise DistributionError(f"missing or symlinked projection source: {path}")
            source_paths.append(path)
        if output in payloads:
            raise DistributionError(f"runtime projection collides with bundle file: {output}")
        normalized = normalize_lifecycle_sources(*source_paths)
        payloads[output] = (
            json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode()
    return source, destination, payloads


def _skill_source(repo_root: Path, skill_id: str, entry: dict[str, Any]) -> Path:
    source_value = entry.get("source")
    if not isinstance(source_value, str):
        raise DistributionError(f"{skill_id}: missing source")
    source = repo_root / source_value
    if not source.is_dir() or not (source / "SKILL.md").is_file():
        raise DistributionError(f"{skill_id}: missing authored source: {source_value}")
    return source


def _write_projected_metadata(
    generated_skill: Path, contract: dict[str, Any], entry: dict[str, Any]
) -> None:
    metadata = generated_skill / "agents" / "openai.yaml"
    source = metadata.read_text(encoding="utf-8") if metadata.is_file() else ""
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        project_openai_metadata(source, derived_implicit_invocation(contract, entry)),
        encoding="utf-8",
    )


def _copy_bundle(repo_root: Path, bundle_name: str, generated_skill: Path) -> None:
    _, destination, payloads = bundle_payloads(repo_root, bundle_name)
    bundle_dest = generated_skill / destination
    if bundle_dest.exists():
        raise DistributionError(f"runtime bundle collides with authored content: {bundle_dest}")
    for relative, payload in payloads.items():
        output = bundle_dest / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)


def render_surface(repo_root: Path, destination: Path) -> None:
    """Render a complete root-flat surface into an empty destination."""
    contract = load_contract(repo_root)
    expected_runtime_owners(contract)
    if destination.exists():
        raise DistributionError(f"render destination already exists: {destination}")
    destination.mkdir(parents=True)
    source_map: dict[str, str] = {}
    for skill_id, raw_entry in sorted(contract["skills"].items()):
        if not isinstance(raw_entry, dict):
            raise DistributionError(f"{skill_id}: skill entry must be a table")
        source = _skill_source(repo_root, skill_id, raw_entry)
        generated_skill = destination / skill_id
        shutil.copytree(source, generated_skill, symlinks=False)
        _write_projected_metadata(generated_skill, contract, raw_entry)
        bundle_name = raw_entry.get("runtime_bundle")
        if bundle_name is not None:
            if not isinstance(bundle_name, str):
                raise DistributionError(f"{skill_id}: runtime_bundle must be a string")
            _copy_bundle(repo_root, bundle_name, generated_skill)
        source_map[skill_id] = raw_entry["source"]
    (destination / ".source-map.json").write_text(
        json.dumps(source_map, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def compare_trees(expected: Path, actual: Path) -> list[str]:
    """Return exact missing, extra, content, and executable-mode differences."""
    expected_files = _files(expected)
    actual_files = _files(actual)
    errors: list[str] = []
    if set(expected_files) != set(actual_files):
        missing = sorted(set(expected_files) - set(actual_files))
        extra = sorted(set(actual_files) - set(expected_files))
        errors.append(f"generated file set differs; missing={missing} extra={extra}")
    for relative in sorted(set(expected_files) & set(actual_files)):
        if expected_files[relative].read_bytes() != actual_files[relative].read_bytes():
            errors.append(f"generated content differs: {relative}")
        if relative.endswith(".sh"):
            expected_exec = bool(expected_files[relative].stat().st_mode & stat.S_IXUSR)
            actual_exec = bool(actual_files[relative].stat().st_mode & stat.S_IXUSR)
            if expected_exec != actual_exec:
                errors.append(f"generated executable mode differs: {relative}")
    return errors


def validate_portability(surface: Path) -> list[str]:
    """Reject generated resources that rely on repository or provider roots."""
    errors: list[str] = []
    forbidden = ("$PLUGIN_ROOT", "${PLUGIN_ROOT", "$CLAUDE_PLUGIN_ROOT", "${CLAUDE_PLUGIN_ROOT")
    for path in _files(surface).values():
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(surface).as_posix()
        for token in forbidden:
            if token in content:
                errors.append(f"{relative}: assumes provider root {token}")
    return errors


def build_validated_surface(
    repo_root: Path,
    parent: Path,
    renderer: Callable[[Path, Path], None] = render_surface,
    validator: Callable[[Path], list[str]] = validate_portability,
) -> tuple[Path, Path]:
    """Build and validate a complete temporary sibling without touching the live tree."""
    temporary = Path(tempfile.mkdtemp(prefix=".skills.new.", dir=parent))
    staged = temporary / "skills"
    try:
        renderer(repo_root, staged)
        errors = validator(staged)
        if errors:
            raise DistributionError("; ".join(errors))
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return temporary, staged
