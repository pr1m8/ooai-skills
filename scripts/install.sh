#!/usr/bin/env bash
set -euo pipefail

# Install skills/commands/agents/rules directly from a GitHub repo.
#
# Usage:
#   ./scripts/install.sh anthropics/skills
#   ./scripts/install.sh vercel-labs/agent-skills --what skills
#   ./scripts/install.sh PatrickJS/awesome-cursorrules --what rules
#   ./scripts/install.sh https://github.com/owner/repo

pdm run ooai-skills install "$@"
