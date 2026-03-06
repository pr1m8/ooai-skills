# End-to-end loop

This is the “happy path” from zero to having skills visible to Deep Agents.

## 1) Install
```bash
unzip ooai-skills.zip
cd ooai-skills
cp .env.example .env
# edit MinIO endpoint/keys/bucket
pdm add -dG dev -e .
```

## 2) Bootstrap MinIO + verify
```bash
./scripts/bootstrap_minio.sh
./scripts/verify.sh
```

## 3) Ingest skill repos into MinIO (no git)
Recommended: set a GitHub token to avoid rate limits.

```bash
export OOAI_SKILLS_GITHUB_TOKEN="..."
./scripts/ingest_curated_zips.sh "Core general skill catalogs" "Security-focused packs"
```

## 4) Pull to local skill directories
```bash
./scripts/pull.sh
# if you want to force copies instead of symlinks:
./scripts/pull.sh --copy
```

## 5) Confirm locally + in Deep Agents
```bash
pdm run ooai-skills local list
deepagents skills list
```

## Updating later
- Add more repos/categories → run ingestion again → pull again.
- If MinIO already has everything you want → just `pull`.
