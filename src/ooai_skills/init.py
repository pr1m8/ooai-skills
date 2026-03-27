"""Scaffold the full multi-agent directory structure.

Creates directories and config files compatible with:
- Claude Code (.claude/skills/, .claude/commands/, .claude/agents/, .claude/rules/, .claude/hooks/)
- Deep Agents / dotagents (.agents/skills/, .agents/rules/, .agents/context/, .agents/memory/)
- Codex (.agents/skills/, AGENTS.md)
- Gemini (.gemini/rules/, .gemini/settings.json)
- Cursor (.cursor/rules/)
- GitHub Copilot (.github/copilot-instructions.md)
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

# --- Templates ---

_MCP_JSON = """\
{
  "mcpServers": {
    "ooai-skills": {
      "command": "python",
      "args": ["-m", "ooai_skills.mcp_server"]
    }
  }
}
"""

_AGENTS_MD = """\
# AGENTS.md

Entry point for agent runtimes (Deep Agents, Codex, dotagents).

## Skills

Agent skills live in `.agents/skills/` (project-local) and `~/.agents/skills/` (global).
Skills are managed by ooai-skills: `ooai-skills pull --all` to sync from registry.

## Context

Project reference material lives in `.agents/context/`.

## Rules

Behavioral guidelines live in `.agents/rules/`.
"""

_EXAMPLE_SKILL_MD = """\
---
name: example-skill
description: An example skill to demonstrate the SKILL.md format. Delete or replace this.
---

# Example Skill

This is a template. Replace it with your own skill.

## Steps

1. Read the relevant code
2. Do the thing
3. Verify the result
"""

_EXAMPLE_COMMAND_MD = """\
# Example Command

This is a legacy Claude Code command (`.claude/commands/`).
Skills (`.claude/skills/`) are now preferred over commands.

$ARGUMENTS
"""

_EXAMPLE_AGENT_MD = """\
---
name: code-reviewer
description: Reviews code changes for quality, security, and test coverage.
model: claude-sonnet-4-6
---

# Code Reviewer

You are a code review specialist. When invoked, review the provided code for:

1. Security issues (injection, auth bypass, data exposure)
2. Logic errors and edge cases
3. Test coverage gaps
4. API breaking changes

Provide findings with severity ratings: critical, warning, info.
"""

_EXAMPLE_PERSONA_MD = """\
# Code Reviewer

A specialized agent persona for code review tasks.

## Capabilities
- Static analysis of code changes
- Security vulnerability detection
- Test coverage assessment

## When to use
Invoke this persona when reviewing pull requests or code changes.
"""

_GEMINI_SETTINGS = """\
{
  "tools": [],
  "rules": []
}
"""

_COPILOT_INSTRUCTIONS = """\
# Copilot Instructions

This project uses the Agent Skills standard (agentskills.io).

## Skills

Agent skills are stored in:
- `.agents/skills/` (project-local)
- `~/.agents/skills/` (user-global, managed by ooai-skills)

Each skill is a directory containing a `SKILL.md` file with YAML frontmatter
(name, description) and markdown instructions.

## Rules

Project coding rules and conventions live in `.agents/rules/`.
"""

_CURSOR_RULES = """\
# Cursor Rules

This project uses the Agent Skills standard. Skills live in `.agents/skills/`
and `~/.agents/skills/`. Each skill directory contains a `SKILL.md` with
YAML frontmatter and markdown instructions.

Rules and conventions are in `.agents/rules/`.
"""

_CLAUDE_MD_SKILL_SECTION = """
## Agent Skills

Skills are managed by [ooai-skills](https://github.com/ooai/tools/ooai-skills).

```bash
# Pull skills from registry (writes to ~/.agents/skills/ AND ~/.claude/skills/)
ooai-skills pull --all

# Search local skills
ooai-skills local find <pattern>

# Browse curated catalog
ooai-skills curated list

# Create a new skill
ooai-skills create my-skill

# Show installation status
ooai-skills status
```
"""

# --- Directory structure definition ---

# Each entry: (relative_path, is_dir, template_content_or_None)
_STRUCTURE: list[tuple[str, bool, str | None]] = [
    # Claude Code
    (".claude/skills", True, None),
    (".claude/commands", True, None),
    (".claude/agents", True, None),
    (".claude/rules", True, None),
    (".claude/hooks", True, None),
    (".claude/skills/example-skill/SKILL.md", False, _EXAMPLE_SKILL_MD),
    (".claude/commands/example.md", False, _EXAMPLE_COMMAND_MD),
    (".claude/agents/code-reviewer.md", False, _EXAMPLE_AGENT_MD),

    # Deep Agents / dotagents / Codex
    (".agents/skills", True, None),
    (".agents/rules", True, None),
    (".agents/context", True, None),
    (".agents/memory", True, None),
    (".agents/personas", True, None),
    (".agents/specs", True, None),
    (".agents/skills/example-skill/SKILL.md", False, _EXAMPLE_SKILL_MD),
    (".agents/personas/code-reviewer.md", False, _EXAMPLE_PERSONA_MD),

    # Gemini
    (".gemini/rules", True, None),
    (".gemini/settings.json", False, _GEMINI_SETTINGS),

    # Cursor
    (".cursor/rules", True, None),
    (".cursor/rules/skills.mdc", False, _CURSOR_RULES),

    # GitHub Copilot
    (".github/copilot-instructions.md", False, _COPILOT_INSTRUCTIONS),
]


def init_project(
    project_dir: Path,
    *,
    console: Console | None = None,
    with_mcp: bool = True,
    with_claude_md: bool = True,
    with_agents_md: bool = True,
) -> None:
    """Create the full multi-agent directory structure in a project."""
    con = console or Console()
    created: list[str] = []

    # Scaffold directories and template files
    for rel_path, is_dir, template in _STRUCTURE:
        full = project_dir / rel_path
        if is_dir:
            if not full.exists():
                full.mkdir(parents=True, exist_ok=True)
                created.append(f"{rel_path}/")
        else:
            if not full.exists():
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_text(template or "", encoding="utf-8")
                created.append(rel_path)

    # .mcp.json
    if with_mcp:
        mcp_json = project_dir / ".mcp.json"
        if not mcp_json.exists():
            mcp_json.write_text(_MCP_JSON, encoding="utf-8")
            created.append(".mcp.json")
        else:
            con.print("[dim].mcp.json already exists, skipping[/dim]")

    # AGENTS.md (Codex / Deep Agents / dotagents entry point)
    if with_agents_md:
        agents_md = project_dir / "AGENTS.md"
        if not agents_md.exists():
            agents_md.write_text(_AGENTS_MD, encoding="utf-8")
            created.append("AGENTS.md")
        else:
            con.print("[dim]AGENTS.md already exists, skipping[/dim]")

    # CLAUDE.md — append skill section if missing
    if with_claude_md:
        claude_md = project_dir / "CLAUDE.md"
        if claude_md.exists():
            existing = claude_md.read_text(encoding="utf-8")
            if "Agent Skills" not in existing:
                with claude_md.open("a", encoding="utf-8") as f:
                    f.write(_CLAUDE_MD_SKILL_SECTION)
                created.append("CLAUDE.md (appended skill section)")
            else:
                con.print("[dim]CLAUDE.md already has Agent Skills section, skipping[/dim]")
        else:
            claude_md.write_text(
                "# CLAUDE.md\n\nThis file provides guidance to Claude Code (claude.ai/code) "
                "when working with code in this repository.\n" + _CLAUDE_MD_SKILL_SECTION,
                encoding="utf-8",
            )
            created.append("CLAUDE.md")

    # Global directories (user-level)
    home = Path.home()
    for gd in [home / ".agents" / "skills", home / ".claude" / "skills"]:
        gd.mkdir(parents=True, exist_ok=True)

    # Report
    if created:
        con.print("[bold]Created:[/bold]")
        for item in created:
            con.print(f"  [green]+[/green] {item}")
    else:
        con.print("[dim]All directories and files already exist.[/dim]")

    con.print(f"\n[green]Initialized[/green] multi-agent structure in {project_dir}")
    con.print("[dim]Scaffolded for: Claude Code, Deep Agents, Codex, Gemini, Cursor, Copilot[/dim]")
    con.print("[dim]Global dirs ensured: ~/.agents/skills/, ~/.claude/skills/[/dim]")
