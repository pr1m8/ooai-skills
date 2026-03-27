# Agent Conventions: .agents/, Deep Agents, Vercel Skills

The agent skills ecosystem has multiple overlapping conventions. This note maps them.

## .agents/ (dotagents Standard)

A directory-as-context standard that organizes AI agent files to prevent config fragmentation across `.claude/`, `.cursor/`, `.gemini/` folders.

### Directory Structure

```
.agents/
├── rules/              # Behavioral guidelines & coding standards
│   ├── global/         # Apply everywhere
│   └── project/        # Project-specific
├── context/            # Read-only reference data (schemas, APIs)
├── memory/             # Persistent knowledge (ADRs, learned preferences)
├── personas/           # Role-specific agent profiles
│   ├── qa.md
│   └── architect.md
├── skills/             # Agent Skills (SKILL.md standard)
│   └── skill-name/
│       └── SKILL.md
├── specs/              # Current task requirements & PRDs
├── logs/               # Activity trails
└── AGENTS.md           # Entry point & router (project root)
```

### Key Idea

Use a slim `AGENTS.md` in the project root as a router — directs agents to deeper context only when needed. Prevents loading everything into context at once.

### CLI Tools

```bash
brew install dot-agents/tap/dot-agents

dot-agents init              # Initialize .agents/ structure
dot-agents add <project>     # Register a project
dot-agents audit             # Verify which rules apply where
dot-agents doctor            # Diagnose configuration issues
dot-agents sync              # Git-based config synchronization
```

### Supported Agents

Claude Code, Cursor, Codex, VS Code Copilot, OpenCode.

---

## Deep Agents Framework

LangChain/LangGraph-based agent harness. Opinionated, batteries-included.

### Key Repos

| Repo | What |
|------|------|
| `langchain-ai/deepagents` | Python harness |
| `langchain-ai/deepagentsjs` | TypeScript implementation |
| `langchain-ai/deep-agents-ui` | UI layer |
| `langchain-ai/deep-agents-from-scratch` | Educational curriculum |

### Directory Convention

Deep Agents uses `~/.deepagents/` (not `~/.agents/`):

```
~/.deepagents/
├── agent/              # Default agent directory
│   ├── AGENTS.md       # Long-term memory/context
│   ├── skills/         # Custom skills
│   └── agents/         # Custom sub-agents
├── history.jsonl       # Command history
└── threads.db          # SQLite persistence
```

### Core Capabilities

- Planning and task decomposition (`write_todos`)
- Filesystem operations (read, write, edit, ls, glob, grep)
- Subagent delegation with isolated contexts
- MCP support via `langchain-mcp-adapters`
- Pluggable backends (in-memory, local disk, LangGraph stores, sandboxes)

### How It Reads Skills

Deep Agents discovers skills from local directories — including `~/.agents/skills/`, which is exactly where ooai-skills outputs.

---

## Vercel Skills CLI (`npx skills`)

Package manager for agent skills. Installs skills from GitHub repos into local directories.

### Commands

```bash
npx skills add vercel-labs/agent-skills   # Install from GitHub
npx skills add ./local-skills             # Install from local path
npx skills list                           # List installed skills
npx skills find <query>                   # Search available skills
npx skills remove <skill>                 # Remove a skill
npx skills update                         # Update all skills
npx skills init <name>                    # Create a new skill
```

### Installation Scopes

| Scope | Flag | Location | Use case |
|-------|------|----------|----------|
| Project | (default) | `./<agent>/skills/` | Team-shared |
| Global | `-g` | `~/<agent>/skills/` | Personal, all projects |

### Sources

GitHub shorthand (`owner/repo`), full URLs, GitLab, git URLs, local paths.

### Relationship to ooai-skills

Vercel CLI *installs* skills. ooai-skills *curates, caches, and distributes* skills. They serve different roles:

| Aspect | Vercel CLI | ooai-skills |
|--------|-----------|-------------|
| Source | GitHub repos directly | MinIO registry (curated + cached) |
| Discovery | `npx skills find` | `ooai-skills local find` / `curated list` |
| Caching | None (direct install) | MinIO + local skillpacks |
| Deduplication | None | SHA256 content hash |
| Offline | No | Yes (after initial pull) |
| Curated catalog | No | Yes (136+ repos, 14 categories) |

---

## Convention Conflicts

Different agents use different directory conventions. No single standard yet.

| Convention | Path | Used by |
|-----------|------|---------|
| `~/.agents/skills/` | Global user skills | dotagents, Codex, ooai-skills output |
| `~/.claude/skills/` | Global user skills | Claude Code |
| `~/.deepagents/` | Agent config + skills | Deep Agents framework |
| `.agents/skills/` | Project-local skills | dotagents, Codex |
| `.claude/skills/` | Project-local skills | Claude Code |
| `.cursor/rules/` | Project rules | Cursor |

### Implication

A skill installed at `~/.agents/skills/foo/` is visible to Codex and Deep Agents but NOT to Claude Code (which reads `~/.claude/skills/`). Bridging is needed — see [INTEGRATION_MAP](INTEGRATION_MAP.md).

## How ooai-skills Relates

- We output to `~/.agents/skills/` — the dotagents/Codex convention
- Deep Agents reads from local dirs — our output is compatible
- Claude Code reads from a different path — needs bridging
- Our curated catalog (136+ repos) is the unique value we add over any of these tools individually
- Vercel CLI could be an alternative ingest source, but our ZIP/git ingest covers the same repos
