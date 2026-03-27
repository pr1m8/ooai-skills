#!/usr/bin/env bash
set -euo pipefail

# Install skills from curated categories directly from GitHub (no MinIO).
#
# Usage:
#   ./scripts/install_curated.sh "Core general skill catalogs"
#   ./scripts/install_curated.sh "Cursor rules" "Windsurf rules"
#   ./scripts/install_curated.sh  # (no args = list categories)
#
# Notes:
#   - Downloads directly from GitHub, no MinIO needed.
#   - Installs skills, commands, agents, and rules.

if [ $# -eq 0 ]; then
  echo "Available categories:"
  pdm run ooai-skills curated categories
  echo ""
  echo "Usage: $0 <category> [category2] ..."
  exit 0
fi

for category in "$@"; do
  echo "=== Installing from category: $category ==="
  repos=$(pdm run ooai-skills curated list --category "$category" --kind skills --kind rules --limit 500 2>/dev/null | grep -oP '[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+' | sort -u || true)
  for repo in $repos; do
    echo "--- $repo ---"
    pdm run ooai-skills install "$repo" || echo "  (skipped: $repo)"
  done
done
