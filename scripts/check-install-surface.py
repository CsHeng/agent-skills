#!/usr/bin/env python3
"""Validate a generated flat skill install surface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import tomllib

REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = REPO_ROOT / "contracts" / "skills.toml"
TARGETS_PATH = REPO_ROOT / "contracts" / "install-targets.toml"
RUNTIME_BUNDLES = {"harness": REPO_ROOT / "src/runtime/harness"}
RUNTIME_EXCLUDED_ROOTS = {"agents", "smoke-test"}


def load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def target_dest(target: str, override: str | None) -> Path:
    if override:
        return (REPO_ROOT / override).resolve()
    targets = load_toml(TARGETS_PATH)["targets"]
    return (REPO_ROOT / targets[target]["dest"]).resolve()


def selected_entries(target: str) -> dict[str, str]:
    data = load_toml(CONTRACT_PATH)
    expected: dict[str, str] = {}
    for skill_name, entry in sorted(data["skills"].items()):
        if target not in entry.get("install", []):
            continue
        if entry.get("category") == "internal" and target != "root-flat":
            raise ValueError(f"{skill_name}: internal skill cannot be installed for {target}")
        public_id = entry["public_id"]
        if public_id in expected:
            raise ValueError(f"duplicate public_id for {target}: {public_id}")
        expected[public_id] = entry["source"]
    return expected


def selected_runtime_contracts(target: str) -> dict[str, str]:
    data = load_toml(CONTRACT_PATH)
    expected: dict[str, str] = {}
    for entry in data["skills"].values():
        if target not in entry.get("install", []):
            continue
        runtime_contract = entry.get("runtime_contract")
        if runtime_contract:
            expected[entry["public_id"]] = runtime_contract
    return expected


def selected_runtime_bundles(target: str) -> dict[str, str]:
    data = load_toml(CONTRACT_PATH)
    expected: dict[str, str] = {}
    for entry in data["skills"].values():
        if target not in entry.get("install", []):
            continue
        runtime_bundle = entry.get("runtime_bundle")
        if runtime_bundle:
            expected[entry["public_id"]] = runtime_bundle
    return expected


def runtime_bundle_files(bundle_name: str) -> dict[str, Path]:
    source = RUNTIME_BUNDLES.get(bundle_name)
    if source is None or not source.is_dir():
        raise ValueError(f"unknown or missing runtime bundle: {bundle_name}")
    return {
        path.relative_to(source).as_posix(): path
        for path in source.rglob("*")
        if path.is_file()
        and path.relative_to(source).parts[0] not in RUNTIME_EXCLUDED_ROOTS
        and path.name != "SKILL.md"
        and "__pycache__" not in path.relative_to(source).parts
    }


def validate_portable_content(target: str, public_id: str, generated_dir: Path) -> list[str]:
    errors: list[str] = []
    for path in generated_dir.rglob("*"):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative_path = path.relative_to(generated_dir).as_posix()
        if "_harness-libs" in content:
            errors.append(
                f"{target}: {public_id}/{relative_path} references retired sibling runtime"
            )
        provider_roots = (
            "$PLUGIN_ROOT",
            "${PLUGIN_ROOT",
            "$CLAUDE_PLUGIN_ROOT",
            "${CLAUDE_PLUGIN_ROOT",
        )
        for provider_root in provider_roots:
            if provider_root in content:
                errors.append(
                    f"{target}: {public_id}/{relative_path} assumes provider root {provider_root}"
                )
        first_use = min(
            (position for token in ("$SKILL_ROOT", "${SKILL_ROOT") if (position := content.find(token)) >= 0),
            default=-1,
        )
        if first_use >= 0:
            assignment = content.find("SKILL_ROOT=")
            if assignment < 0 or assignment > first_use:
                errors.append(
                    f"{target}: {public_id}/{relative_path} uses SKILL_ROOT before assigning it"
                )
    return errors


def validate(target: str, dest: Path) -> list[str]:
    errors: list[str] = []
    skills_dir = dest if target == "root-flat" else dest / "skills"
    if not skills_dir.is_dir():
        return [f"missing skills directory: {skills_dir.relative_to(REPO_ROOT)}"]

    try:
        expected = selected_entries(target)
        runtime_bundles = selected_runtime_bundles(target)
    except (KeyError, ValueError) as exc:
        return [str(exc)]

    actual = sorted(path.name for path in skills_dir.iterdir() if path.is_dir())
    expected_ids = sorted(expected)
    if actual != expected_ids:
        errors.append(f"{target}: skill directories differ; expected={expected_ids} actual={actual}")

    for public_id in expected_ids:
        skill_file = skills_dir / public_id / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{target}: missing SKILL.md for {public_id}")
            continue

        source_dir = REPO_ROOT / expected[public_id]
        generated_dir = skills_dir / public_id
        source_files = {
            path.relative_to(source_dir).as_posix(): path
            for path in source_dir.rglob("*")
            if path.is_file()
        }
        runtime_bundle = runtime_bundles.get(public_id)
        if runtime_bundle:
            try:
                bundle_files = runtime_bundle_files(runtime_bundle)
            except ValueError as exc:
                errors.append(f"{target}: {public_id}: {exc}")
                continue
            for relative_path, source_file in bundle_files.items():
                bundled_path = f"scripts/harness/{relative_path}"
                if bundled_path in source_files:
                    errors.append(
                        f"{target}: runtime bundle collides with authored file for "
                        f"{public_id}/{bundled_path}"
                    )
                    continue
                source_files[bundled_path] = source_file
        generated_files = {
            path.relative_to(generated_dir).as_posix(): path
            for path in generated_dir.rglob("*")
            if path.is_file()
        }
        if set(source_files) != set(generated_files):
            errors.append(
                f"{target}: generated files differ for {public_id}; "
                f"expected={sorted(source_files)} actual={sorted(generated_files)}"
            )
            continue
        for relative_path, source_file in source_files.items():
            if source_file.read_bytes() != generated_files[relative_path].read_bytes():
                errors.append(
                    f"{target}: generated content differs for {public_id}/{relative_path}"
                )
        errors.extend(validate_portable_content(target, public_id, generated_dir))

    for public_id, runtime_contract in selected_runtime_contracts(target).items():
        contract_file = skills_dir / public_id / runtime_contract
        if not contract_file.is_file():
            errors.append(f"{target}: missing runtime contract for {public_id}: {runtime_contract}")

    source_map_path = skills_dir / ".source-map.json"
    if not source_map_path.is_file():
        errors.append(f"{target}: missing .source-map.json")
    else:
        try:
            source_map = json.loads(source_map_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{target}: invalid .source-map.json: {exc}")
        else:
            if source_map != expected:
                errors.append(f"{target}: .source-map.json differs from manifest selection")

    return errors


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=["claude", "codex", "root-flat"], required=True)
    parser.add_argument("--dest", help="Override destination")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    errors = validate(args.target, target_dest(args.target, args.dest))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"{args.target} install surface ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
