#!/usr/bin/env bash
set -euo pipefail

# Push a local folder of skills into MinIO.
#
# Usage:
#   ./scripts/push_local.sh /path/to/skills-root my-pack

ROOT="${1:?missing skills root}"
PACK="${2:-manual}"

pdm run ooai-skills push-local "${ROOT}" --pack "${PACK}"
