#!/usr/bin/env bash
set -euo pipefail

# Install repository git hooks into .git/hooks/.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

install_hook() {
  local name="$1"
  local src="$repo_root/hooks/$name"
  local dst="$repo_root/.git/hooks/$name"
  chmod +x "$src"
  ln -sf "$src" "$dst"
  echo "installed $name -> $dst"
}

install_hook pre-commit
