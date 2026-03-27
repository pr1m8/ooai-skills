# End-to-end loop

This is the "happy path" from zero to having skills visible to Deep Agents and Claude Code.

## 1) Install
```bash
cd ooai-skills
cp .env.example .env
# edit MinIO endpoint/keys/bucket if needed
pdm install
```

## 2) Scaffold project structure
```bash
pdm run ooai-skills init .
```
Creates `.claude/` (skills, commands, agents, rules, hooks), `.agents/` (skills, rules, context, memory), `.gemini/`, `AGENTS.md`, and `.mcp.json`.

## 3) Bootstrap MinIO
```bash
./scripts/bootstrap_minio.sh
```

## 4) Ingest skill repos into MinIO (no git)
Recommended: set a GitHub token to avoid rate limits.

```bash
export OOAI_SKILLS_GITHUB_TOKEN="..."
./scripts/ingest_curated_zips.sh "Core general skill catalogs" "Security-focused packs"
```

## 5) Pull to local skill directories
```bash
./scripts/pull.sh
# if you want to force copies instead of symlinks:
./scripts/pull.sh --copy
```

By default, pull writes to both `~/.agents/skills/` (Deep Agents / Codex) and `~/.claude/skills/` (Claude Code).

## 6) Confirm locally
```bash
pdm run ooai-skills local list
ls ~/.agents/skills/
ls ~/.claude/skills/
```

## Updating later
- Add more repos/categories → run ingestion again → pull again.
- If MinIO already has everything you want → just `pull`.
