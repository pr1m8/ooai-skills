# MinIO registry

## Environment variables
See `.env.example`. Minimum required:

- `OOAI_SKILLS_S3_ENDPOINT` (e.g. `http://localhost:9000`)
- `OOAI_SKILLS_S3_ACCESS_KEY`
- `OOAI_SKILLS_S3_SECRET_KEY`
- `OOAI_SKILLS_BUCKET`

## Bucket bootstrap
```bash
./scripts/bootstrap_minio.sh
```

This script uses `mc` to:
- set an alias
- create the bucket if missing
- enable versioning (best effort)

## Registry objects
- `packs/...` contains the mirrored skill folders
- `index/skills.json` drives `pull`

If you upload objects manually (outside ooai-skills), they will not be pulled until the index is updated.
Prefer using ooai-skills ingestion commands or `push-local` so the index stays accurate.
