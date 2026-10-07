#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
diagram_dir="$repo_root/docs/architecture/diagrams"
generated_dir="$repo_root/docs/architecture/generated"
check_mode=0
if [[ "${1:-}" == "--check" ]]; then
  check_mode=1
  shift
fi
if [[ $# -gt 0 ]]; then
  echo "usage: $(basename "$0") [--check]" >&2
  exit 2
fi

plantuml_cmd="${PLANTUML:-${RENDER_DIAGRAMS_PLANTUML:-}}"
if [[ -z "$plantuml_cmd" ]]; then
  if command -v plantuml >/dev/null 2>&1; then
    plantuml_cmd="plantuml"
  else
    echo "ERROR: PlantUML is required; declare or install the product tool." >&2
    exit 1
  fi
fi

shopt -s nullglob
puml_files=("$diagram_dir"/*.puml)
if [[ ${#puml_files[@]} -eq 0 ]]; then
  echo "ERROR: no diagram sources under $diagram_dir" >&2
  exit 1
fi

scratch="$(mktemp -d "${TMPDIR:-/tmp}/render-diagrams.XXXXXX")"
# shellcheck disable=SC2329
cleanup() {
  if [[ -n "$scratch" && -d "$scratch" ]]; then
    rm -rf "$scratch"
  fi
}
trap cleanup EXIT

errors=0
for puml in "${puml_files[@]}"; do
  base="$(basename "$puml" .puml)"
  expected_svg="$generated_dir/$base.svg"
  work="$scratch/$base"
  mkdir -p "$work"
  if ! "$plantuml_cmd" -tsvg -o "$work" "$puml"; then
    echo "ERROR: PlantUML failed for $(basename "$puml")" >&2
    if [[ "$check_mode" -eq 1 ]]; then
      errors=1
      continue
    fi
    exit 1
  fi
  rendered="$work/$base.svg"
  if [[ ! -f "$rendered" ]]; then
    echo "ERROR: missing rendered output for $base" >&2
    if [[ "$check_mode" -eq 1 ]]; then
      errors=1
      continue
    fi
    exit 1
  fi
  if [[ "$check_mode" -eq 1 ]]; then
    if [[ ! -f "$expected_svg" ]] || ! cmp -s "$rendered" "$expected_svg"; then
      echo "ERROR: stale or missing generated diagram: docs/architecture/generated/$base.svg" >&2
      errors=1
    fi
  else
    mkdir -p "$generated_dir"
    publish="$scratch/publish-$base.svg"
    cp "$rendered" "$publish"
    mv -f "$publish" "$expected_svg"
  fi
done

exit "$errors"
