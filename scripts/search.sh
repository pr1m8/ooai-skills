#!/usr/bin/env bash
set -euo pipefail

# Search for skills — locally and in the remote registry.
#
# Usage:
#   ./scripts/search.sh deploy           # search local
#   ./scripts/search.sh deploy --remote  # search MinIO registry

if [[ "${2:-}" == "--remote" ]]; then
  pdm run ooai-skills remote search "$1"
else
  pdm run ooai-skills local find "$1"
fi
