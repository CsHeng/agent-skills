#!/usr/bin/env bash
# Render reader-facing decision maps; does not run agents or validate policy semantics.
set -euo pipefail

if [[ $# -ne 0 ]]; then
  echo "usage: $(basename "$0")" >&2
  exit 2
fi
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_dir="$repo_root/docs/architecture/diagrams/decisions"
output_dir="$repo_root/docs/architecture/generated/decisions"
dot_cmd="${DOT:-dot}"
if ! command -v "$dot_cmd" >/dev/null 2>&1; then
  echo "ERROR: Graphviz dot is required to render decision maps." >&2
  exit 1
fi
shopt -s nullglob
sources=("$source_dir"/*.dot)
if [[ ${#sources[@]} -eq 0 ]]; then
  echo "ERROR: no decision diagram sources under $source_dir" >&2
  exit 1
fi
scratch="$(mktemp -d "${TMPDIR:-/tmp}/decision-diagrams.XXXXXX")"
trap 'rm -rf "$scratch"' EXIT
mkdir -p "$output_dir"
for source in "${sources[@]}"; do
  name="$(basename "$source" .dot)"
  "$dot_cmd" -Tsvg "$source" -o "$scratch/$name.svg"
  mv -f "$scratch/$name.svg" "$output_dir/$name.svg"
done
