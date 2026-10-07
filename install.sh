#!/usr/bin/env bash
# Install the SDD skill for Claude Code and Codex by symlinking skill/sdd.
# Edits in this repository are live in both tools; nothing is copied.
#
#   ./install.sh              install (or confirm) both symlinks
#   ./install.sh --uninstall  remove symlinks that point at this repository
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/skill/sdd"
TARGETS=("$HOME/.claude/skills/sdd" "$HOME/.codex/skills/sdd")
MODE="${1:-install}"

[ -f "$SRC/SKILL.md" ] || { echo "error: $SRC/SKILL.md not found" >&2; exit 1; }

for target in "${TARGETS[@]}"; do
  tool_home="$(dirname "$(dirname "$target")")"   # ~/.claude or ~/.codex
  if [ "$MODE" = "--uninstall" ]; then
    if [ -L "$target" ] && [ "$(readlink "$target")" = "$SRC" ]; then
      rm "$target" && echo "removed  $target"
    else
      echo "skipped  $target (not a link to this repository)"
    fi
    continue
  fi
  if [ ! -d "$tool_home" ]; then
    echo "skipped  $target ($tool_home not found: tool not installed?)"
    continue
  fi
  if [ -L "$target" ]; then
    if [ "$(readlink "$target")" = "$SRC" ]; then
      echo "ok       $target (already installed)"
    else
      echo "error: $target links to $(readlink "$target"); remove it first" >&2
      exit 1
    fi
    continue
  fi
  if [ -e "$target" ]; then
    echo "error: $target exists and is not a symlink; refusing to overwrite" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$target")"
  ln -s "$SRC" "$target"
  echo "linked   $target -> $SRC"
done
