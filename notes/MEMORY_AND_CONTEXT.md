# Memory and Context Systems

How AI agents load persistent instructions, learned knowledge, and scoped rules.

## CLAUDE.md (User-Written Instructions)

Persistent instructions loaded at every session start. The primary way to shape Claude Code behavior.

### Loading Order

| Priority | File | Scope | Version control |
|----------|------|-------|----------------|
| 1 | `~/.claude/CLAUDE.md` | User (all projects) | Personal |
| 2 | `CLAUDE.md` (project root) | Team | Committed |
| 3 | `CLAUDE.local.md` (project root) | Personal | Gitignored |
| 4 | Subdirectory `CLAUDE.md` files | On-demand | Committed |

### Import Syntax

CLAUDE.md supports `@path/to/file` imports to stay modular:

```markdown
# Project Instructions

@docs/ARCHITECTURE.md
@.claude/rules/testing-standards.md
```

Imported files expand inline. Useful for keeping CLAUDE.md under the recommended 200-line limit.

### What Goes in CLAUDE.md

- Build/test/lint commands
- Architecture overview (big-picture, not discoverable from reading one file)
- Team conventions that Claude should follow
- Pointers to key files and their roles

### What Does NOT Go in CLAUDE.md

- Things Claude can discover by reading the code (file structure, imports, types)
- Generic advice ("write clean code", "add tests")
- Secrets or credentials

---

## Auto-Memory (Claude-Written Learnings)

Written by Claude during sessions. Not edited by the user.

### Location

```
~/.claude/projects/<project-hash>/memory/
├── MEMORY.md           # Index file
├── user_role.md        # Topic: who the user is
├── feedback_testing.md # Topic: testing preferences
├── project_auth.md     # Topic: auth rewrite context
└── ...
```

### Loading Behavior

| File | When loaded | Budget |
|------|------------|--------|
| `MEMORY.md` | Session start | First 200 lines (or 25KB) |
| Topic files (`*.md`) | On-demand when relevant | Full content |

### Memory Types

| Type | What it captures | Example |
|------|-----------------|---------|
| `user` | Role, preferences, expertise | "Senior engineer, deep Go expertise, new to React" |
| `feedback` | Corrections and confirmations | "Don't mock DB in integration tests" |
| `project` | Ongoing work, deadlines, decisions | "Auth rewrite driven by compliance, not tech debt" |
| `reference` | Pointers to external systems | "Pipeline bugs tracked in Linear project INGEST" |

### Memory File Format

```markdown
---
name: feedback_testing
description: User prefers real DB in integration tests
type: feedback
---

Integration tests must hit a real database, not mocks.

**Why:** Prior incident where mock/prod divergence masked a broken migration.
**How to apply:** Any test file under tests/integration/ should use the real DB fixture.
```

### Key Properties

- Machine-local (not shared across devices)
- All worktrees in same repo share one memory directory
- Claude verifies memories against current code before acting on them
- Stale memories get updated or removed

---

## Rules (`.claude/rules/`)

Modular instruction files that load automatically based on context.

### Path Scoping

Rules can target specific files via frontmatter globs:

```markdown
---
globs: src/backend/**/*.py
---

# Backend Rules

- Use SQLAlchemy async sessions
- All endpoints must validate auth token
```

This rule only loads when backend Python files are in context.

### Global Rules

Rules without `globs:` frontmatter load for every session. Equivalent to content in CLAUDE.md but organized as separate files.

---

## AGENTS.md (Cross-Agent Convention)

Used by Deep Agents and the dotagents standard. Similar purpose to CLAUDE.md but agent-agnostic.

- Lives at project root or inside `.agents/`
- Deep Agents uses it for long-term memory/context
- Codex reads it as project instructions
- Some projects maintain both `CLAUDE.md` and `AGENTS.md` for different agent runtimes

---

## Context Budget

All persistent context competes for the same context window:

| Source | Approximate cost |
|--------|-----------------|
| CLAUDE.md (all levels) | ~200-500 tokens per file |
| Rules (loaded) | ~100-300 tokens per rule |
| Memory index (MEMORY.md) | First 200 lines |
| Skill descriptions | ~100 tokens per skill |
| Full skill body (when activated) | < 5000 tokens recommended |
| MCP tool definitions | ~8,700 tokens total (with Tool Search) |

Progressive disclosure is the key pattern: load metadata cheaply, full content only when needed.

## How ooai-skills Relates

- Our `CLAUDE.md` documents build commands and architecture for Claude Code sessions
- Skills we curate should respect the 5000-token instruction budget per skill
- Our `discover.py` only reads frontmatter + body from SKILL.md — we don't currently track or measure token cost
- Future: could add a lint rule for skills exceeding the 5000-token recommendation
