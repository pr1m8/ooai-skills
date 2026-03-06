# Troubleshooting

## GitHub rate limits / 403 during ZIP ingestion
- Set `OOAI_SKILLS_GITHUB_TOKEN` and pass it via `--github-token` or use the script.

## MinIO connection errors
- Check `.env` endpoint/keys.
- Run `./scripts/verify.sh`.
- Verify MinIO is reachable from the machine.

## `pull` builds symlinks but your tool can’t follow them
- Use `ooai-skills pull --all --copy` or `./scripts/pull.sh --copy`.

## Skills missing after manual uploads to MinIO
- ooai-skills pulls only what is in `index/skills.json`.
- Re-ingest using `push-local` or ZIP ingestion to update the index.
