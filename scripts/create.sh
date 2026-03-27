#!/usr/bin/env bash
set -euo pipefail

# Create a new skill, command, agent, or rule from template.
#
# Usage:
#   ./scripts/create.sh my-skill                        # skill (default)
#   ./scripts/create.sh my-command --kind command        # command
#   ./scripts/create.sh my-agent --kind agent            # agent
#   ./scripts/create.sh my-rule --kind rule              # rule

pdm run ooai-skills create "$@"
