# scripts

Helper scripts for setup, installation, and day-to-day workflows.

These scripts do *not* embed secrets. They assume you have a `.env` (or exported env vars).

## Setup

| Script | What it does |
|--------|-------------|
| `init.sh [dir]` | Scaffold multi-agent dirs (Claude Code, Deep Agents, Codex, Gemini, Cursor, Copilot) |
| `bootstrap_minio.sh` | Create MinIO bucket, set alias, enable versioning |

## Direct install (no MinIO needed)

| Script | What it does |
|--------|-------------|
| `install.sh <repo>` | Install skills/commands/agents/rules from any GitHub repo |
| `install_curated.sh <category>` | Install from curated categories directly from GitHub |

## MinIO registry workflow

| Script | What it does |
|--------|-------------|
| `ingest_curated_zips.sh <category>` | Ingest curated repos into MinIO via ZIP (no git) |
| `mirror_curated.sh` | Mirror curated repos into MinIO via git |
| `pull.sh` | Pull from MinIO to local dirs (`~/.agents/skills/` + `~/.claude/skills/`) |
| `push_local.sh <dir>` | Upload local skills to MinIO |
| `export_sources.sh` | Export curated list to sources.yaml |

## Browse & manage

| Script | What it does |
|--------|-------------|
| `status.sh` | Show skill counts across all targets |
| `search.sh <pattern>` | Search local skills (add `--remote` for MinIO) |
| `create.sh <name>` | Create new skill/command/agent/rule from template |

## Quick start (no MinIO)

```bash
# 1. Scaffold project
./scripts/init.sh

# 2. Install official skills directly from GitHub
./scripts/install.sh anthropics/skills
./scripts/install.sh vercel-labs/agent-skills
./scripts/install.sh cloudflare/skills

# 3. Install cursor rules
./scripts/install.sh PatrickJS/awesome-cursorrules --what rules

# 4. Check what's installed
./scripts/status.sh
```

## Quick start (with MinIO)

```bash
# 1. Bootstrap MinIO
./scripts/bootstrap_minio.sh

# 2. Ingest curated repos
./scripts/ingest_curated_zips.sh "Core general skill catalogs" "Security-focused packs"

# 3. Pull to local
./scripts/pull.sh

# 4. Check
./scripts/status.sh
```
