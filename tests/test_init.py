from __future__ import annotations

from pathlib import Path

from ooai_skills.init import init_project


def test_init_creates_structure(tmp_path: Path) -> None:
    """init_project scaffolds all expected directories and files."""
    init_project(tmp_path, with_mcp=True, with_claude_md=True, with_agents_md=True)

    # Claude Code directories
    assert (tmp_path / ".claude" / "skills").is_dir()
    assert (tmp_path / ".claude" / "commands").is_dir()
    assert (tmp_path / ".claude" / "agents").is_dir()
    assert (tmp_path / ".claude" / "rules").is_dir()
    assert (tmp_path / ".claude" / "hooks").is_dir()

    # Deep Agents / dotagents directories
    assert (tmp_path / ".agents" / "skills").is_dir()
    assert (tmp_path / ".agents" / "rules").is_dir()
    assert (tmp_path / ".agents" / "context").is_dir()
    assert (tmp_path / ".agents" / "memory").is_dir()
    assert (tmp_path / ".agents" / "personas").is_dir()
    assert (tmp_path / ".agents" / "specs").is_dir()

    # Gemini
    assert (tmp_path / ".gemini" / "rules").is_dir()
    assert (tmp_path / ".gemini" / "settings.json").is_file()

    # Cursor
    assert (tmp_path / ".cursor" / "rules").is_dir()
    assert (tmp_path / ".cursor" / "rules" / "skills.mdc").is_file()

    # Copilot
    assert (tmp_path / ".github" / "copilot-instructions.md").is_file()

    # Root files
    assert (tmp_path / ".mcp.json").is_file()
    assert (tmp_path / "AGENTS.md").is_file()
    assert (tmp_path / "CLAUDE.md").is_file()

    # Example skills
    assert (tmp_path / ".claude" / "skills" / "example-skill" / "SKILL.md").is_file()
    assert (tmp_path / ".agents" / "skills" / "example-skill" / "SKILL.md").is_file()

    # Example command and agent
    assert (tmp_path / ".claude" / "commands" / "example.md").is_file()
    assert (tmp_path / ".claude" / "agents" / "code-reviewer.md").is_file()
    assert (tmp_path / ".agents" / "personas" / "code-reviewer.md").is_file()


def test_init_idempotent(tmp_path: Path) -> None:
    """Running init twice doesn't overwrite existing files."""
    init_project(tmp_path)

    # Modify a file
    mcp = tmp_path / ".mcp.json"
    mcp.write_text('{"custom": true}', encoding="utf-8")

    # Run again
    init_project(tmp_path)

    # Should not overwrite
    assert '"custom"' in mcp.read_text(encoding="utf-8")


def test_init_appends_claude_md(tmp_path: Path) -> None:
    """init appends skill section to existing CLAUDE.md."""
    claude_md = tmp_path / "CLAUDE.md"
    claude_md.write_text("# Existing\n\nSome content.\n", encoding="utf-8")

    init_project(tmp_path)

    content = claude_md.read_text(encoding="utf-8")
    assert "Existing" in content
    assert "Agent Skills" in content


def test_init_no_mcp(tmp_path: Path) -> None:
    """--no-mcp skips .mcp.json creation."""
    init_project(tmp_path, with_mcp=False)
    assert not (tmp_path / ".mcp.json").exists()
