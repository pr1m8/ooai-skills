#!/usr/bin/env bash
set -euo pipefail

# Bootstrap a MinIO bucket using the MinIO Client (mc).
#
# Requirements:
#   - `mc` installed
#   - env vars set (or `.env` sourced):
#       OOAI_SKILLS_S3_ENDPOINT
#       OOAI_SKILLS_S3_ACCESS_KEY
#       OOAI_SKILLS_S3_SECRET_KEY
#       OOAI_SKILLS_BUCKET
#
# Usage:
#   ./scripts/bootstrap_minio.sh

: "${OOAI_SKILLS_S3_ENDPOINT:?missing OOAI_SKILLS_S3_ENDPOINT}"
: "${OOAI_SKILLS_S3_ACCESS_KEY:?missing OOAI_SKILLS_S3_ACCESS_KEY}"
: "${OOAI_SKILLS_S3_SECRET_KEY:?missing OOAI_SKILLS_S3_SECRET_KEY}"
: "${OOAI_SKILLS_BUCKET:?missing OOAI_SKILLS_BUCKET}"

ALIAS_NAME="ooai"

mc alias set "${ALIAS_NAME}" "${OOAI_SKILLS_S3_ENDPOINT}" "${OOAI_SKILLS_S3_ACCESS_KEY}" "${OOAI_SKILLS_S3_SECRET_KEY}"

# Create bucket if missing.
mc mb --ignore-existing "${ALIAS_NAME}/${OOAI_SKILLS_BUCKET}"

# Try to enable versioning (safe to fail on older MinIO setups).
mc version enable "${ALIAS_NAME}/${OOAI_SKILLS_BUCKET}" || true

echo "OK: bucket ready: ${ALIAS_NAME}/${OOAI_SKILLS_BUCKET}"
