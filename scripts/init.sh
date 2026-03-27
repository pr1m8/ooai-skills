#!/usr/bin/env bash
set -euo pipefail

# Scaffold multi-agent directory structure in the current project.
#
# Usage:
#   ./scripts/init.sh
#   ./scripts/init.sh /path/to/project

pdm run ooai-skills init "${1:-.}"
