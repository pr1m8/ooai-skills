#!/usr/bin/env bash
set -euo pipefail

# Mirror curated categories into MinIO (requires mirror-capable variant).
#
# Usage:
#   ./scripts/mirror_curated.sh "Core general skill catalogs" "Security-focused packs"

if ! pdm run ooai-skills --help | grep -q "mirror-curated"; then
  echo "This package variant does not include Git mirroring."
  echo "Use push-local, or install the mirror/full variant."
  exit 2
fi

ARGS=()
for c in "$@"; do
  ARGS+=( --category "$c" )
done

pdm run ooai-skills mirror-curated "${ARGS[@]}" --kinds skills
