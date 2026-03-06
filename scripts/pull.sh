#!/usr/bin/env bash
set -euo pipefail

# Pull everything from MinIO into ~/.agents/skillpacks + ~/.agents/skills.
#
# Usage:
#   ./scripts/pull.sh
#   ./scripts/pull.sh --copy

pdm run ooai-skills pull --all "$@"
