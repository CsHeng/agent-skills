#!/usr/bin/env python3
"""Generate flat skill install surfaces from the structured source tree."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import TypedDict

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from skill_activation import derived_implicit_invocation, project_openai_metadata

CONTRACT_PATH = REPO_ROOT / "contracts" / "skills.toml"
TARGETS_PATH = REPO_ROOT / "contracts" / "install-targets.toml"
RUNTIME_BUNDLES = {"harness": REPO_ROOT / "src/runtime/harness"}
RUNTIME_EXCLUDED_ROOTS = {"agents", "smoke-test"}


class SkillEntry(TypedDict, total=False):
    source: str
    public_id: str
    category: str
    install: list[str]
    runtime_bundle: str
    activation_mode: str


class TargetEntry(TypedDict, total=False):
    dest: str
    include_internal_runtime_support: bool


def load_toml(path: Path) -> dict[str, object]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_skills(data: dict[str, object] | None = None) -> dict[str, SkillEntry]:
    if data is None:
        data = load_toml(CONTRACT_PATH)
    skills = data.get("skills")
    if not isinstance(skills, dict):
        raise SystemExit("contracts/skills.toml must contain [skills.*] entries")
    return skills  # type: ignore[return-value]


def load_targets() -> dict[str, TargetEntry]:
    data = load_toml(TARGETS_PATH)
    targets = data.get("targets")
    if not isinstance(targets, dict):
        raise SystemExit("contracts/install-targets.toml must contain [targets.*] entries")
    return targets  # type: ignore[return-value]


def selected_skills(skills: dict[str, SkillEntry], target: str) -> list[SkillEntry]:
    selected: list[SkillEntry] = []
    seen_public_ids: set[str] = set()
    for skill_name, entry in sorted(skills.items()):
        install_targets = entry.get("install", [])
        public_id = entry.get("public_id")
        source = entry.get("source")
        if target not in install_targets:
            continue
        if not public_id or not source:
            raise SystemExit(f"skill {skill_name} is missing public_id or source")
        if public_id in seen_public_ids:
            raise SystemExit(f"duplicate public_id selected for {target}: {public_id}")
        seen_public_ids.add(public_id)
        selected.append(entry)
    return selected


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def replace_directory(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    backup: Path | None = None
    if dest.exists() or dest.is_symlink():
        backup = Path(tempfile.mkdtemp(prefix=f".{dest.name}.old.", dir=str(dest.parent)))
        backup.rmdir()
        dest.rename(backup)
    try:
        source.rename(dest)
    except BaseException:
        if backup is not None and not dest.exists():
            backup.rename(dest)
        raise
    else:
        if backup is not None:
            remove_path(backup)


def copy_runtime_bundle(bundle_name: str, dest: Path) -> None:
    source = RUNTIME_BUNDLES.get(bundle_name)
    if source is None:
        raise SystemExit(f"unknown runtime bundle: {bundle_name}")
    if not source.is_dir():
        raise SystemExit(f"missing runtime bundle source: {source.relative_to(REPO_ROOT)}")
    if dest.exists() or dest.is_symlink():
        raise SystemExit(f"runtime bundle destination already exists: {dest}")

    copied = 0
    for source_file in sorted(source.rglob("*")):
        relative_path = source_file.relative_to(source)
        if relative_path.parts[0] in RUNTIME_EXCLUDED_ROOTS:
            continue
        if source_file.name == "SKILL.md" or "__pycache__" in relative_path.parts:
            continue
        if source_file.is_symlink():
            raise SystemExit(
                f"runtime bundle source must not contain symlinks: "
                f"{source_file.relative_to(REPO_ROOT)}"
            )
        if not source_file.is_file():
            continue
        destination_file = dest / relative_path
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination_file)
        copied += 1

    if copied == 0:
        raise SystemExit(f"runtime bundle has no production files: {bundle_name}")


def assert_portable_content(public_id: str, generated_skill: Path) -> None:
    for path in generated_skill.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative_path = path.relative_to(generated_skill).as_posix()
        if "_harness-libs" in content:
            raise SystemExit(
                f"{public_id}/{relative_path} references retired sibling runtime"
            )
        provider_roots = (
            "$PLUGIN_ROOT",
            "${PLUGIN_ROOT",
            "$CLAUDE_PLUGIN_ROOT",
            "${CLAUDE_PLUGIN_ROOT",
        )
        for provider_root in provider_roots:
            if provider_root in content:
                raise SystemExit(
                    f"{public_id}/{relative_path} assumes provider root {provider_root}"
                )
        first_use = min(
            (
                position
                for token in ("$SKILL_ROOT", "${SKILL_ROOT")
                if (position := content.find(token)) >= 0
            ),
            default=-1,
        )
        if first_use >= 0:
            assignment = content.find("SKILL_ROOT=")
            if assignment < 0 or assignment > first_use:
                raise SystemExit(
                    f"{public_id}/{relative_path} uses SKILL_ROOT before assigning it"
                )


def generate_target(target: str, dest: Path) -> None:
    contract = load_toml(CONTRACT_PATH)
    skills = load_skills(contract)
    selected = selected_skills(skills, target)
    tmp_parent = REPO_ROOT / ".tmp-install"
    tmp_parent.mkdir(exist_ok=True)
    tmp_dir = Path(tempfile.mkdtemp(prefix=f"{target}.", dir=str(tmp_parent)))
    tmp_dest = tmp_dir / "surface"
    skills_dest = tmp_dest if target == "root-flat" else tmp_dest / "skills"
    skills_dest.mkdir(parents=True)

    source_map: dict[str, str] = {}
    try:
        for entry in selected:
            public_id = entry["public_id"]
            source_rel = entry["source"]
            source_path = REPO_ROOT / source_rel
            if not source_path.is_dir():
                raise SystemExit(f"missing source directory for {public_id}: {source_rel}")
            if not (source_path / "SKILL.md").is_file():
                raise SystemExit(f"missing SKILL.md for {public_id}: {source_rel}")
            generated_skill = skills_dest / public_id
            shutil.copytree(source_path, generated_skill, symlinks=False)
            metadata_path = generated_skill / "agents" / "openai.yaml"
            try:
                metadata_source = metadata_path.read_text(encoding="utf-8")
            except OSError:
                metadata_source = ""
            metadata_path.parent.mkdir(parents=True, exist_ok=True)
            metadata_path.write_text(
                project_openai_metadata(
                    metadata_source,
                    derived_implicit_invocation(contract, entry),
                ),
                encoding="utf-8",
            )
            runtime_bundle = entry.get("runtime_bundle")
            if runtime_bundle:
                copy_runtime_bundle(
                    runtime_bundle,
                    generated_skill / "scripts/harness",
                )
            assert_portable_content(public_id, generated_skill)
            source_map[public_id] = source_rel

        with (skills_dest / ".source-map.json").open("w", encoding="utf-8") as handle:
            json.dump(source_map, handle, indent=2, sort_keys=True)
            handle.write("\n")

        replace_directory(tmp_dest, dest)
    finally:
        remove_path(tmp_dir)


def target_dest(target: str, override: str | None) -> Path:
    if override:
        return (REPO_ROOT / override).resolve()
    targets = load_targets()
    entry = targets.get(target)
    if not entry or "dest" not in entry:
        raise SystemExit(f"unknown target: {target}")
    return (REPO_ROOT / entry["dest"]).resolve()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["claude", "codex", "root-flat", "all"], required=True)
    parser.add_argument("--dest", help="Override destination for single-target generation")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.target == "all":
        if args.dest:
            raise SystemExit("--dest cannot be used with --target all")
        for target in ("claude", "codex", "root-flat"):
            generate_target(target, target_dest(target, None))
        return 0
    generate_target(args.target, target_dest(args.target, args.dest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
