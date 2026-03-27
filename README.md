# ooai-skills

[![Python 3.13+](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen.svg)](#testing)
[![Ruff](https://img.shields.io/badge/linter-ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![Agent Skills](https://img.shields.io/badge/standard-SKILL.md-blueviolet.svg)](https://agentskills.io)

Multi-agent skills registry: ingest, cache, and distribute [SKILL.md](https://agentskills.io) skills across **Claude Code, Deep Agents, Codex, Cursor, Copilot, Gemini, Windsurf**, and more.

## Features

- **90+ curated repos** across 18 categories — official vendor skills, community mega-packs, cursor rules, MCP servers
- **Direct install from GitHub** — `ooai-skills install anthropics/skills` (no MinIO needed)
- **MinIO/S3 registry** — ingest, cache, and pull with SHA256 deduplication
- **Multi-target output** — writes to `~/.agents/skills/` AND `~/.claude/skills/` by default
- **Handles everything** — skills, commands, agents, rules (routes to correct directories automatically)
- **MCP server** — exposes skill browsing as MCP tools for any compatible agent
- **Full scaffold** — `ooai-skills init` creates dirs for Claude Code, Deep Agents, Codex, Gemini, Cursor, and Copilot
- **Comprehensive linting** — validates name format, description length, token budget, unknown frontmatter keys
- **Selective pull** — by name (`--name deploy`) or category (`--category "Cursor rules"`)

## Architecture

```
GitHub repos (90+ curated)
       │
       ├──── ooai-skills install ──── Direct to local (no MinIO)
       │
       └──── ooai-skills ingest ──── MinIO/S3 registry
                                         │
                                    ooai-skills pull
                                         │
                          ┌──────────────┼──────────────┐
                          ▼              ▼              ▼
                   ~/.agents/skills  ~/.claude/skills  (extra targets)
                   (Deep Agents,     (Claude Code)
                    Codex)
```

## Quick Start (no MinIO)

```bash
# Install
pip install -e .

# Scaffold project structure
ooai-skills init .

# Install skills from GitHub
ooai-skills install anthropics/skills
ooai-skills install vercel-labs/agent-skills
ooai-skills install PatrickJS/awesome-cursorrules --what rules

# Check what's installed
ooai-skills status

# Search
ooai-skills local find deploy
```

## Quick Start (with MinIO)

```bash
cp .env.example .env      # Edit MinIO credentials
./scripts/bootstrap_minio.sh

# Ingest curated repos
./scripts/ingest_curated_zips.sh "Core general skill catalogs"

# Pull to local
ooai-skills pull --all

# Search the remote registry
ooai-skills remote search kubernetes
```

## CLI Reference

### Setup & Scaffold

| Command | Description |
|---------|-------------|
| `init [dir]` | Scaffold multi-agent dirs (Claude Code, Deep Agents, Codex, Gemini, Cursor, Copilot) |
| `create <name> [--kind skill\|command\|agent\|rule]` | Create new item from template |
| `status` | Show skill counts across all targets |

### Install (direct from GitHub)

| Command | Description |
|---------|-------------|
| `install <repo>` | Install skills/commands/agents/rules from any GitHub repo |
| `install <repo> --what skills` | Install only skills |
| `install <repo> --what rules` | Install only rules |

### Registry (MinIO)

| Command | Description |
|---------|-------------|
| `pull --all` | Pull all skills from registry |
| `pull --name <skill>` | Pull a single skill by name |
| `pull --category <cat>` | Pull only skills from a curated category |
| `push-local <dir>` | Upload local skills to MinIO |
| `mirror <sources.yaml>` | Mirror repos via git clone |
| `ingest-github-zip <repo>` | Ingest via ZIP archive (no git) |
| `remote stats` | Show registry stats |
| `remote search <pattern>` | Search the remote index |

### Browse

| Command | Description |
|---------|-------------|
| `local list` | List installed skills |
| `local find <pattern>` | Search by name/description |
| `local info <name>` | Show skill details |
| `local cat <name>` | View SKILL.md content |
| `local remove <name>` | Remove an installed skill |
| `curated categories` | List curated categories |
| `curated list` | Browse the curated catalog (90+ repos) |

### MCP Server

```bash
ooai-skills mcp-serve   # Start stdio MCP server
```

Or configure in `.mcp.json`:
```json
{
  "mcpServers": {
    "ooai-skills": {
      "command": "python",
      "args": ["-m", "ooai_skills.mcp_server"]
    }
  }
}
```

Exposes tools: `list_skills`, `find_skills`, `get_skill_info`, `read_skill`.

## Curated Catalog

90+ repos across 18 categories:

| Category | Repos | Examples |
|----------|-------|---------|
| Core general skill catalogs | 6 | anthropics/skills, openai/skills, microsoft/skills |
| Cursor rules | 6 | PatrickJS/awesome-cursorrules (100+), sanjeed5/awesome-cursor-rules-mdc (879+) |
| Community mega-packs | 9 | sickn33/antigravity-awesome-skills (1304+), alirezarezvani/claude-skills (192+) |
| Claude Code resources | 6 | rohitg00/awesome-claude-code-toolkit, travisvn/awesome-claude-skills |
| MCP servers | 4 | TensorBlock/awesome-mcp-servers (7260+), wong2/awesome-mcp-servers |
| Windsurf rules | 3 | SchneiderSam/awesome-windsurfrules |
| Copilot instructions | 2 | github/awesome-copilot (175+ agents, 208+ skills) |
| Cross-agent coding rules | 4 | block/ai-rules, obviousworks/agentic-coding-rulebook |
| + 10 more categories | ... | Cloud, databases, ML/AI, security, web/frontend, ... |

Browse the full catalog: `ooai-skills curated list`

## Supported Agents

| Agent | Skills | Commands | Agents | Rules | MCP |
|-------|--------|----------|--------|-------|-----|
| Claude Code | `.claude/skills/` | `.claude/commands/` | `.claude/agents/` | `.claude/rules/` | `.mcp.json` |
| Deep Agents | `.agents/skills/` | — | `.agents/personas/` | `.agents/rules/` | — |
| Codex | `.agents/skills/` | — | — | `.agents/rules/` | — |
| Gemini | — | — | — | `.gemini/rules/` | — |
| Cursor | — | — | — | `.cursor/rules/` | — |
| Copilot | — | — | — | `.github/copilot-instructions.md` | — |

## Configuration

Environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `OOAI_SKILLS_S3_ENDPOINT` | `http://localhost:9000` | MinIO endpoint |
| `OOAI_SKILLS_S3_ACCESS_KEY` | `minioadmin` | S3 access key |
| `OOAI_SKILLS_S3_SECRET_KEY` | `minioadmin` | S3 secret key |
| `OOAI_SKILLS_BUCKET` | `agent-skills` | Bucket name |
| `OOAI_SKILLS_EXTRA_TARGETS` | `~/.claude/skills` | Comma-separated extra output dirs |

## Testing

```bash
pdm install
pdm run pytest -v          # Run all tests
pdm run ruff check src/    # Lint
```

## Documentation

- [Command Reference](docs/COMMANDS.md)
- [End-to-End Guide](docs/E2E.md)
- [Concepts](docs/CONCEPTS.md)
- [MinIO Setup](docs/MINIO.md)
- [Research Notes](notes/INDEX.md) — ecosystem knowledge base

## License

MIT
