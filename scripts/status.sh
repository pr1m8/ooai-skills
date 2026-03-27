#!/usr/bin/env bash
set -euo pipefail

# Show skill installation status across all targets.
#
# Usage:
#   ./scripts/status.sh

pdm run ooai-skills status
