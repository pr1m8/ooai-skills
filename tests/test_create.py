"""Tests for the create command (skill, command, agent, rule)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _run_create(tmp_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "ooai_skills", "create", *args],
        cwd=tmp_path, capture_output=True, text=True,
    )


def test_create_skill(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "my-skill")
    assert result.returncode == 0
    assert (tmp_path / ".claude/skills/my-skill/SKILL.md").exists()
    assert (tmp_path / ".agents/skills/my-skill/SKILL.md").exists()
    content = (tmp_path / ".claude/skills/my-skill/SKILL.md").read_text()
    assert "name: my-skill" in content


def test_create_command(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "run-tests", "--kind", "command")
    assert result.returncode == 0
    assert (tmp_path / ".claude/commands/run-tests.md").exists()


def test_create_agent(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "code-reviewer", "--kind", "agent")
    assert result.returncode == 0
    assert (tmp_path / ".claude/agents/code-reviewer.md").exists()
    assert (tmp_path / ".agents/personas/code-reviewer.md").exists()


def test_create_rule(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "no-console", "--kind", "rule")
    assert result.returncode == 0
    assert (tmp_path / ".claude/rules/no-console.md").exists()
    assert (tmp_path / ".agents/rules/no-console.md").exists()


def test_create_skill_claude_only(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "deploy", "--target", "claude")
    assert result.returncode == 0
    assert (tmp_path / ".claude/skills/deploy/SKILL.md").exists()
    assert not (tmp_path / ".agents/skills/deploy/SKILL.md").exists()


def test_create_invalid_name(tmp_path: Path) -> None:
    result = _run_create(tmp_path, "Bad_Name")
    assert result.returncode == 1


def test_create_idempotent(tmp_path: Path) -> None:
    _run_create(tmp_path, "my-skill")
    result = _run_create(tmp_path, "my-skill")
    assert result.returncode == 0  # should succeed, just skip existing
    assert "Already exists" in result.stdout
