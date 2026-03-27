# Integration Map: ooai-skills and the Ecosystem

How our system connects to each piece of the agent skills ecosystem — what works today, what doesn't, and what to build next.

## Current State

### What ooai-skills Does Today

```
GitHub repos (136+ curated)
       │
       ▼
  ooai-skills ingest (ZIP or git clone)
       │
       ▼
  MinIO/S3 (index/skills.json + packs/<owner>/<repo>/<path>/)
       │
       ▼
  ooai-skills pull --all
       │
       ├──► ~/.agents/skillpacks/   (cache, preserves repo structure)
       └──► ~/.agents/skills/       (flattened symlink view)
```

- Ingests SKILL.md repos from GitHub via ZIP archive or shallow git clone
- Stores in MinIO under content-addressed prefixes with three index files
- Pulls to local cache + flattened symlink view
- SHA256 deduplication prevents redundant uploads
- Lints for missing name/description (FM001/FM002) and oversized files (SZ001)

### What Consumes Our Output Today

| Consumer | Path it reads | Status |
|----------|-------------|--------|
| Deep Agents | `~/.agents/skills/` | Works — auto-discovers SKILL.md |
| Codex | `~/.agents/skills/` | Works — same convention |
| Any agent pointed at the directory | `~/.agents/skills/` | Works |

### What Does NOT Consume Our Output (Yet)

| Consumer | Path it reads | Gap |
|----------|-------------|-----|
| Claude Code | `~/.claude/skills/` | Different directory convention |
| Cursor | `.cursor/rules/` | Different format entirely |
| VS Code Copilot | `.github/copilot-instructions.md` + skills | Different config surface |

---

## Integration Points

### ooai-skills → Claude Code

Claude Code reads from `~/.claude/skills/` and `.claude/skills/`, not `~/.agents/skills/`.

| Option | How | Trade-off |
|--------|-----|-----------|
| **Symlink bridge** | `ln -s ~/.agents/skills ~/.claude/skills` | Simple; Claude Code may not follow symlinks into symlinked dirs |
| **Dual pull target** | Add `--target` flag, pull to both `~/.agents/skills/` and `~/.claude/skills/` | Native; clean separation; doubles disk usage |
| **Change default** | Set `OOAI_SKILLS_LOCAL_SKILLS=~/.claude/skills` | Picks one consumer; breaks Deep Agents |
| **CLAUDE.md pointer** | Import skills via `@~/.agents/skills/foo/SKILL.md` in CLAUDE.md | No file duplication; but not auto-discovered as skills |

**Recommendation:** Dual pull target (`--target`) is the cleanest. Our `sync.py:pull_all()` already takes `settings` with configurable output paths — adding a second target is straightforward.

### ooai-skills → Deep Agents

Already works. `pull --all` outputs to `~/.agents/skills/` which Deep Agents auto-discovers.

### ooai-skills → Vercel Skills CLI

| Direction | How |
|-----------|-----|
| Vercel → ooai | Use `npx skills` as an ingest source (alternative to GitHub ZIP) |
| ooai → Vercel | Use our curated catalog to seed `npx skills add` installations |

Low priority — our ZIP ingest already covers the same GitHub repos.

### ooai-skills → .agents/ Project Convention

Two valid scopes:
- **Global** (`~/.agents/skills/`): Shared across all projects — what `ooai-skills pull` produces
- **Project-local** (`.agents/skills/`): Custom skills for one project — managed manually or via `push-local`

### ooai-skills → MCP

**Future: MCP server wrapping our local commands.**

| CLI command | MCP tool equivalent |
|-------------|-------------------|
| `ooai-skills local list` | `list_skills()` |
| `ooai-skills local find <pattern>` | `find_skills(pattern)` |
| `ooai-skills local info <name>` | `get_skill_info(name)` |
| `ooai-skills local cat <name>` | `read_skill(name)` |

This would let any MCP-compatible agent search and load skills at runtime — not just at session start.

---

## Gaps and Next Steps

| Gap | What's missing | Effort | Priority |
|-----|---------------|--------|----------|
| Claude Code target | `--target` flag for pull to output to `~/.claude/skills/` | Small — extend `pull_all()` and CLI | High |
| Frontmatter extensions | Add Claude Code extension fields (`paths`, `effort`, `context`) to high-value curated skills | Medium — needs per-skill review | Medium |
| MCP skill server | MCP server exposing `list/find/info/cat` as tools | Medium — new module + server scaffold | Medium |
| Token budget lint | Warn when SKILL.md body exceeds 5000 tokens | Small — add to `discover.py` lint | Medium |
| Multi-agent output | Detect installed agents, output to all their conventions | Large — agent detection + config | Future |
| Validation extensions | Validate Claude Code extension frontmatter, not just base standard | Small — extend lint in `discover.py` | Low |
| Skill versioning | Track skill versions across ingest cycles | Medium — extend `SkillRecord` model | Future |

---

## Key Code Paths

| Component | File | What to modify for integration |
|-----------|------|-------------------------------|
| Pull pipeline | `src/ooai_skills/sync.py` | `pull_all()` — add multi-target support |
| CLI pull command | `src/ooai_skills/cli.py` | `cmd_pull()` — add `--target` option |
| Settings | `src/ooai_skills/settings.py` | Add `local_claude_skills_dir` field |
| Skill discovery | `src/ooai_skills/discover.py` | Extend linting for token budget + extensions |
| Data models | `src/ooai_skills/models.py` | `SkillRecord` — add version field if needed |
| Local browsing | `src/ooai_skills/local.py` | Wrap as MCP server tools |
