#!/usr/bin/env bash
set -euo pipefail

# Ingest curated repo categories using GitHub archive ZIP downloads (no git).
#
# Usage:
#   ./scripts/ingest_curated_zips.sh "Core general skill catalogs" "Security-focused packs"
#
# Notes:
#   - Uses 'OOAI_SKILLS_GITHUB_TOKEN' if set to avoid rate limits.
#   - Only ingests repos of kind=skills by default; adjust below if needed.

TOKEN="${OOAI_SKILLS_GITHUB_TOKEN:-}"

ARGS=()
for c in "$@"; do
  ARGS+=( --category "$c" )
done

if [ -n "$TOKEN" ]; then
  pdm run ooai-skills ingest-curated-zips "${ARGS[@]}" --kinds skills --github-token "$TOKEN"
else
  pdm run ooai-skills ingest-curated-zips "${ARGS[@]}" --kinds skills
fi
