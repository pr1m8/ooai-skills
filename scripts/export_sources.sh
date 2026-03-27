#!/usr/bin/env bash
set -euo pipefail

# Export the embedded curated list into a sources.yaml (for mirror variants).
#
# Usage:
#   ./scripts/export_sources.sh sources.yaml

OUT="${1:-sources.yaml}"
pdm run ooai-skills curated export "${OUT}" --kinds skills --all-categories
echo "Wrote: ${OUT}"
