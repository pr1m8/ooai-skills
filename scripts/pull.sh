#!/usr/bin/env bash
set -euo pipefail

# Pull skills from MinIO into ~/.agents/skills + ~/.claude/skills.
#
# Usage:
#   ./scripts/pull.sh                          # pull all
#   ./scripts/pull.sh --copy                   # copies instead of symlinks
#   ./scripts/pull.sh --name deploy-app        # pull single skill by name
#   ./scripts/pull.sh --category "Cursor rules"  # pull only one category
#   ./scripts/pull.sh --no-extra               # skip ~/.claude/skills target

pdm run ooai-skills pull --all "$@"
