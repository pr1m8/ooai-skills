# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

ooai-skills is a multi-agent skills registry. It ingests SKILL.md skills from GitHub repos (directly or via MinIO/S3) and distributes them to `~/.agents/skills/` (Deep Agents/Codex), `~/.claude/skills/` (Claude Code), and other agent directories. Handles skills, commands, agents, and rules — routing each to the correct location.

## Build & Development

```bash
pdm install                              # Install all deps
pdm run pytest -v                        # Run tests (38+)
pdm run ruff check src/ tests/           # Lint
pdm run ruff format src/ tests/          # Format
python -m ooai_skills <command>          # Run CLI
```

Ruff: line-length 100, target Python 3.13.

## Architecture

**Two install paths:**
- `install <repo>` — direct GitHub download, no MinIO needed (`direct.py`)
- `pull --all` — download from MinIO registry (`sync.py`)

**Registry (MinIO):** Three index files at `index/skills.json`, `index/sources.json`, `index/lint.json`. Skill content under `packs/<owner>/<repo>/<path>/`. SHA256 deduplication. Integrity verification on download.

**Multi-target:** `pull` writes to `~/.agents/skills/` + `~/.claude/skills/` by default. Configurable via `OOAI_SKILLS_EXTRA_TARGETS` env var.

**Selective pull:** `pull --name <skill>` for single skill, `pull --category <cat>` for category filter.

**Generalized installer:** `direct.py` handles skills (SKILL.md), commands (.md), agents (.md), and rules (.md/.mdc/.cursorrules) — routes each to the correct target directory.

**Discovery + linting:** `discover.py` finds SKILL.md files, parses frontmatter, hashes content, and validates (FM001/FM002 missing fields, SZ001 size, TK001 token budget, EXT001 unknown keys, NM001/NM002 name format/match, DESC001 description length).

**CLI:** Typer app. Top-level: `init`, `create`, `status`, `install`, `pull`, `push-local`, `mirror`, `mcp-serve`. Sub-groups: `curated`, `local`, `remote`.

**Init scaffold:** Creates dirs for Claude Code, Deep Agents, Codex, Gemini, Cursor, and Copilot. Includes example skills, commands, agents, personas, and rules.

**MCP server:** `mcp_server.py` — stdio JSON-RPC server exposing `list_skills`, `find_skills`, `get_skill_info`, `read_skill`. Searches both `~/.agents/skills/` and `~/.claude/skills/`.

## Key Files

- `cli.py` — All CLI commands (Typer)
- `direct.py` — Generalized GitHub installer (skills, commands, agents, rules)
- `sync.py` — MinIO pull + multi-target rebuild + single-skill pull + remote search
- `discover.py` — Skill discovery + comprehensive linting (9 lint rules)
- `models.py` — Pydantic models: `SkillRecord`, `SkillIndex`, `RepoSource`, `CuratedRepo`, `LintIssue`
- `s3.py` — `S3Client` with upload notifications + presigned URLs
- `init.py` — Multi-agent scaffold (6 agent runtimes)
- `mcp_server.py` — MCP server (stdio) with multi-path browsing
- `curated.py` + `data/curated.json` — Embedded catalog (90+ repos, 18 categories)
- `frontmatter.py` — YAML frontmatter parser
- `settings.py` — `OoaiSkillsSettings` (pydantic-settings, env vars, extra targets)
