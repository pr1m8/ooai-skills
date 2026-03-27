# Claude Code Infrastructure — E2E

Complete reference for the `.claude/` folder system, permission model, and session loading.

## Overview

- Three scope levels: **project**, **user**, **enterprise**
- Everything driven by files on disk — no cloud config
- Deterministic loading order at session start
- Higher scopes override lower scopes for permissions; skills merge across all scopes

---

## Project-Level

Files in `.claude/` and the project root. Version-controlled unless noted.

### `.claude/settings.json` (team permissions)

Shared across the team. Committed to git.

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "deny": ["Bash(rm -rf *)"]
  },
  "env": {
    "NODE_ENV": "development"
  }
}
```

Key fields: `permissions.allow[]`, `permissions.deny[]`, `env`, `mcpServers`, `enabledMcpjsonServers`, `enableAllProjectMcpServers`.

### `.claude/settings.local.json` (personal overrides)

Same schema as `settings.json`. Gitignored. Merged at runtime — local overrides team settings.

### `.claude/rules/` (modular instructions)

Markdown files that replace or supplement `CLAUDE.md`:

- **Global rules:** `rules/style.md` — loaded for every session
- **Path-scoped rules:** `rules/backend.md` with `globs: src/backend/**` frontmatter — loaded only when matching files are in context
- Alternative to a monolithic CLAUDE.md for large projects

### `.claude/commands/` (legacy slash commands)

Markdown files that become `/command-name`. Supports `$ARGUMENTS` substitution. Being superseded by skills — new projects should use `.claude/skills/` instead.

### `.claude/skills/` (project skills)

SKILL.md directories following the agentskills.io standard plus Claude Code extensions. See [CLAUDE_CODE_SKILLS](CLAUDE_CODE_SKILLS.md).

- Auto-invoked based on description matching or `paths:` globs
- Project-scoped: available only in this project
- Claude indexes skill names + descriptions at session start (cheap: ~100 tokens each)
- Full skill content loaded on-demand when activated

### `.claude/agents/` (subagent personas)

Markdown files defining specialized subagents:

- Own model override, tool scope, system prompt
- Independent context windows (preserves main context)
- Three built-in types: `Explore`, `Plan`, `general-purpose`
- Skills can target a specific agent type via `agent:` frontmatter

### `.claude/hooks/` (event-driven automation)

Deterministic automation — guaranteed execution, not LLM suggestions. Configured in `settings.json` under the `hooks` key.

**Events:**

| Event | When it fires |
|-------|--------------|
| `PreToolUse` | Before a tool executes |
| `PostToolUse` | After a tool completes |
| `SessionStart` | Session initialization |
| `Stop` | Agent finishes response |
| `Notification` | Claude sends an alert |
| `UserPromptSubmit` | User submits input |
| `SubagentStop` | Subagent finishes |

**Use cases:** run linter after every edit, load context at session start, enforce project rules, integrate CI checks.

### `CLAUDE.md` (project root)

Team instructions. Committed to version control. Loaded at every session start.

- Supports `@path/to/file` imports for modularity
- Best practice: keep under 200 lines per file
- Parent directory CLAUDE.md files also load at startup; subdirectory ones load on-demand

### `CLAUDE.local.md` (project root)

Personal project notes. Gitignored. Same format as CLAUDE.md.

### `.mcp.json` (project root)

MCP server configurations for the project. See [MCP](MCP.md).

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "some-mcp-server"],
      "env": { "API_KEY": "..." }
    }
  }
}
```

---

## User-Level (`~/.claude/`)

Personal configuration applied across all projects.

### `~/.claude/CLAUDE.md`

Personal preferences. Loaded before project-level CLAUDE.md.

### `~/.claude/settings.json`

User-level permissions. Merged with project settings (deny always wins).

### `~/.claude/settings.local.json`

User-local overrides. Same schema.

### `~/.claude/skills/`

Personal skills available across all projects. Same SKILL.md format. Higher priority than project skills on name collision.

### `~/.claude/rules/`

Personal rules applied to all projects.

### `~/.claude/projects/<project>/memory/`

Auto-memory system — written by Claude, not the user.

| File | Purpose | Loading |
|------|---------|---------|
| `MEMORY.md` | Index file | First 200 lines loaded at session start |
| `*.md` (topic files) | Detailed notes by topic | Loaded on-demand when relevant |

Machine-local. All worktrees in same repo share one memory directory.

---

## Enterprise-Level

Managed policies that override everything else.

| OS | Path |
|----|------|
| macOS | `/Library/Application Support/ClaudeCode/` |
| Linux | `/etc/claude-code/` |

Format: `managed-settings.json`. Deployed via MDM or system admin. Cannot be overridden by user or project settings.

---

## Permission Model

Three states: **Deny**, **Ask**, **Allow**.

**Resolution order:** Deny > Ask > Allow (deny always wins).

**Merge order across scopes:**
1. Enterprise managed policy (highest priority)
2. User settings (`~/.claude/settings.json`)
3. Project settings (`.claude/settings.json`)
4. Project-local overrides (`.claude/settings.local.json`)

A deny at any level cannot be overridden by an allow at a lower level.

---

## Skill Scope Resolution

Skills are discovered from all three scopes and merged:

| Priority | Scope | Path |
|----------|-------|------|
| 1 (highest) | Enterprise | `/Library/Application Support/ClaudeCode/skills/` |
| 2 | Personal | `~/.claude/skills/<skill-name>/SKILL.md` |
| 3 | Project | `.claude/skills/<skill-name>/SKILL.md` |

On name collision, higher scope wins. Subdirectories in monorepos are auto-discovered.

---

## Session Start Loading Order

What happens when Claude Code starts a session:

1. Enterprise managed policy loaded
2. User settings loaded (`~/.claude/settings.json` + `settings.local.json`)
3. Project settings loaded (`.claude/settings.json` + `settings.local.json`)
4. Permission model resolved (deny > ask > allow across all scopes)
5. CLAUDE.md files loaded (user → project → local, with `@imports` expanded)
6. Auto-memory index loaded (first 200 lines of `MEMORY.md`)
7. Rules loaded for files currently in context (glob-matched)
8. MCP servers initialized (`.mcp.json` + settings)
9. Skills indexed — names + descriptions from all scopes injected into system prompt
10. Hooks registered for their respective events

---

## What This Means for ooai-skills

Our system outputs to `~/.agents/skills/` (Deep Agents convention). Claude Code reads from `~/.claude/skills/` and `.claude/skills/`.

**Bridging options:**

| Option | How | Trade-off |
|--------|-----|-----------|
| Symlink | `ln -s ~/.agents/skills/ ~/.claude/skills` | Simple; breaks if either side moves |
| Multi-target pull | `ooai-skills pull --all --target ~/.claude/skills/` | Native; requires adding target flag |
| CLAUDE.md reference | Point CLAUDE.md at `~/.agents/skills/` via `@` import | No file duplication; Claude reads but doesn't auto-discover as skills |
| Dual output | Configure `OOAI_SKILLS_LOCAL_SKILLS=~/.claude/skills` | Replaces Deep Agents output; pick one consumer |
