# Claude Code Skills and Slash Commands

Claude Code extends the base SKILL.md standard with proprietary frontmatter keys, dynamic substitutions, and a slash-command system. This note covers all of it.

## Skills as Slash Commands

Every skill with a `name` becomes a `/slash-command` in Claude Code:

- Skill at `.claude/skills/deploy/SKILL.md` with `name: deploy` → user types `/deploy`
- Skills also auto-invoke when Claude decides the task matches the `description`
- Legacy `.claude/commands/*.md` files also create slash commands but lack frontmatter control

### Commands vs Skills

| Feature | Commands (`.claude/commands/`) | Skills (`.claude/skills/`) |
|---------|-------------------------------|---------------------------|
| Format | Plain markdown | SKILL.md with frontmatter |
| Slash command | Yes (`/command-name`) | Yes (`/skill-name`) |
| Auto-invocation | No — user must invoke | Yes — Claude can invoke based on description |
| Subagent support | No | Yes (`context: fork`) |
| Tool restrictions | No | Yes (`allowed-tools`) |
| Path scoping | No | Yes (`paths` globs) |
| Supporting files | No | Yes (scripts/, references/, assets/) |

**Commands are legacy.** New projects should use skills exclusively.

## Extension Frontmatter Keys

Beyond the base SKILL.md standard fields (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`):

### Invocation Control

| Key | Default | Effect |
|-----|---------|--------|
| `disable-model-invocation: true` | `false` | Only user can invoke via `/name` — Claude cannot auto-invoke |
| `user-invocable: false` | `true` | Only Claude can invoke — skill hidden from slash-command menu |

**When to use each:**
- `disable-model-invocation` → side-effect operations (deploy, send email, delete resources)
- `user-invocable: false` → background knowledge (coding standards, domain context)

### Execution Context

| Key | Values | Effect |
|-----|--------|--------|
| `context: fork` | `fork` | Run in isolated subagent with own context window |
| `agent` | `Explore`, `Plan`, `general-purpose` | Which subagent type to use (requires `context: fork`) |
| `effort` | `low`, `medium`, `high`, `max` | Thinking effort level |
| `model` | Model ID string | Override the session's model for this skill |
| `shell` | `bash`, `powershell` | Shell for command execution |

### Auto-Activation

| Key | Value | Effect |
|-----|-------|--------|
| `paths` | Glob patterns (list) | Skill only auto-activates when matching files are in context |

Without `paths`, a skill is always eligible for auto-invocation (unless `user-invocable: false`).

### Lifecycle

| Key | Value | Effect |
|-----|-------|--------|
| `hooks` | Hook config | Lifecycle hooks specific to this skill |
| `argument-hint` | String | Autocomplete hint shown in slash-command UI |

## Dynamic Substitutions

Available in the SKILL.md body — replaced at invocation time:

| Substitution | Expands to |
|-------------|-----------|
| `$ARGUMENTS` | Full argument string passed to the skill |
| `$1`, `$2`, ... `$N` | Positional arguments |
| `$ARGUMENTS[0]`, `$ARGUMENTS[1]` | Same as `$1`, `$2` (alternate syntax) |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Absolute path to the skill's directory on disk |

## Command Substitution

Shell commands in the SKILL.md body execute before Claude sees the prompt:

```markdown
Here are the current staged changes:

!`git diff --cached`

Review these changes and suggest improvements.
```

The `` !`command` `` syntax runs the command and inlines its stdout. Useful for injecting dynamic context.

## Complete Example

```yaml
---
name: review-pr
description: Review a pull request for code quality, security issues, and test coverage.
disable-model-invocation: true
context: fork
agent: Explore
effort: high
paths:
  - "**/*.py"
  - "**/*.ts"
allowed-tools: Read Grep Glob Bash
argument-hint: <PR number or URL>
---

# PR Review

Review PR $1 thoroughly.

Current branch status:
!`git status --short`

## Steps

1. Read the PR diff
2. Check for security issues (injection, auth bypass, data exposure)
3. Verify test coverage for changed code
4. Check for breaking API changes
5. Summarize findings with severity ratings
```

## Skill Discovery Locations

| Priority | Scope | Path |
|----------|-------|------|
| 1 (highest) | Enterprise | `/Library/Application Support/ClaudeCode/skills/` (macOS) |
| 2 | Personal | `~/.claude/skills/<skill-name>/SKILL.md` |
| 3 | Project | `.claude/skills/<skill-name>/SKILL.md` |
| 4 | Nested | `./<subdir>/.claude/skills/<skill-name>/SKILL.md` (monorepo auto-discovery) |

## How ooai-skills Relates

Our curated skills follow the base SKILL.md standard. Claude Code extension fields are optional — they are ignored by non-Claude agents, so they are safe to include.

**Decisions for our system:**
- Should we add Claude Code extensions (paths, effort, context) to high-value curated skills?
- Should we validate extension fields during lint, or only base standard fields?
- Should `ooai-skills pull` have a `--target ~/.claude/skills/` mode for direct Claude Code integration?
