# SKILL.md Standard (agentskills.io)

The portable, cross-agent standard for defining agent skills. Supported by 40+ agents including Claude Code, Cursor, Codex, Copilot, OpenCode, Cline, Windsurf, and more.

## Core Concept

Any directory containing a `SKILL.md` file is a skill. The file combines YAML frontmatter (metadata) with a markdown body (instructions).

## SKILL.md Format

```yaml
---
name: my-skill-name
description: What this skill does and when an agent should use it.
license: MIT
compatibility: Requires network access for API calls.
metadata:
  author: org-name
  version: "1.0"
allowed-tools: Read Grep Bash
---

# Instructions

Step-by-step instructions, examples, edge cases...
```

## Frontmatter Schema

| Field | Required | Constraints | Purpose |
|-------|----------|-------------|---------|
| `name` | Yes | 1-64 chars, lowercase + hyphens, must match directory name | Unique identifier, becomes `/slash-command` in some agents |
| `description` | Yes | 1-1024 chars | Tells agent **what** it does and **when** to use it; used for auto-invocation |
| `license` | No | License name or file reference | Rights information |
| `compatibility` | No | Max 500 chars | System requirements, network needs, intended agent |
| `metadata` | No | Key-value mapping | Custom properties (author, version, tags) |
| `allowed-tools` | No | Space-delimited list | Which tools the skill may use (experimental, varies by agent) |

## Directory Structure

```
skill-name/
├── SKILL.md              # Required — metadata + instructions
├── scripts/              # Optional — executable code (Python, Bash, JS)
├── references/           # Optional — detailed docs, loaded on-demand
│   ├── REFERENCE.md
│   └── API_GUIDE.md
└── assets/               # Optional — templates, images, data files
    ├── templates/
    └── data/
```

## Progressive Disclosure

Skills load in three stages to manage context budget:

| Stage | What loads | Token cost | When |
|-------|-----------|------------|------|
| **Metadata** | `name` + `description` from frontmatter | ~100 tokens per skill | Always (session start) |
| **Instructions** | Full SKILL.md body | < 5000 tokens recommended | When skill activates |
| **Resources** | scripts/, references/, assets/ | Varies | On-demand, when instructions reference them |

This means hundreds of skills can be indexed cheaply, with full content loaded only when needed.

## Validation

The `skills-ref` CLI validates structure and frontmatter:

```bash
skills-ref validate ./my-skill
```

## Best Practices

- Keep SKILL.md body under 500 lines / 5000 tokens
- Move reference material to `references/` — use relative paths: `[guide](references/REFERENCE.md)`
- File references should stay one directory level deep
- Write descriptions that answer "when should an agent use this?" not just "what does this do?"
- The `name` field must match the directory name exactly

## How ooai-skills Uses This

| Component | What it does |
|-----------|-------------|
| `discover.py` | Recursively finds `SKILL.md` files via `rglob("SKILL.md")` |
| `frontmatter.py` | Parses YAML frontmatter (handles UTF-8 BOM, safe YAML) |
| `hashing.py` | Computes SHA256 of entire skill directory for deduplication |
| `models.py` | `SkillRecord.frontmatter` preserves all frontmatter fields as dict |

**Lint codes we enforce:**

| Code | Severity | Meaning |
|------|----------|---------|
| FM001 | Warning | Missing `name` in frontmatter |
| FM002 | Warning | Missing `description` in frontmatter |
| SZ001 | Error | SKILL.md exceeds 10MB |

We currently check `name` and `description` only. We do not enforce `license`, `compatibility`, or the name-matches-directory constraint from the full spec.
