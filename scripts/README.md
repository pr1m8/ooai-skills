# scripts

Small helper scripts for day-1 setup and repeatable workflows.

These scripts are intentionally boring: they do *not* embed secrets.
They assume you have a `.env` (or exported environment variables).

Recommended env vars (see `.env.example`):
- `OOAI_SKILLS_S3_ENDPOINT`
- `OOAI_SKILLS_S3_ACCESS_KEY`
- `OOAI_SKILLS_S3_SECRET_KEY`
- `OOAI_SKILLS_BUCKET`

## ZIP ingestion
- `ingest_curated_zips.sh`: ingest curated repos via GitHub archive ZIP downloads (no git).
