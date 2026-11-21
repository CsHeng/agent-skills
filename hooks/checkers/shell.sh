#!/usr/bin/env bash
set -euo pipefail

FILE="$1"

INTERP="bash"
if head -1 "$FILE" | grep -q "zsh"; then
  INTERP="zsh"
elif head -1 "$FILE" | grep -q "bin/sh"; then
  INTERP="sh"
fi

"$INTERP" -n "$FILE" 2>&1 | head -20 || true

if command -v shellcheck >/dev/null 2>&1; then
  shellcheck "$FILE" 2>&1 | head -30 || true
fi
