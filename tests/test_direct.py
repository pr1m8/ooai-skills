"""Tests for the generalized installer (direct.py)."""
from __future__ import annotations

from pathlib import Path

from ooai_skills.direct import (
    _discover_agents,
    _discover_commands,
    _discover_rules,
)


def _make_tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def test_discover_commands(tmp_path: Path) -> None:
    _make_tree(tmp_path, {
        "commands/deploy.md": "# Deploy",
        ".claude/commands/test.md": "# Test",
        "other/file.txt": "not a command",
    })
    found = _discover_commands(tmp_path)
    names = {p.name for p in found}
    assert "deploy.md" in names
    assert "test.md" in names
    assert "file.txt" not in names


def test_discover_agents(tmp_path: Path) -> None:
    _make_tree(tmp_path, {
        ".claude/agents/reviewer.md": "# Review",
        "personas/qa.md": "# QA",
    })
    found = _discover_agents(tmp_path)
    names = {p.name for p in found}
    assert "reviewer.md" in names
    assert "qa.md" in names


def test_discover_rules(tmp_path: Path) -> None:
    _make_tree(tmp_path, {
        ".claude/rules/style.md": "# Style",
        ".cursor/rules/react.mdc": "# React",
        ".agents/rules/backend.md": "# Backend",
        "rules/global.md": "# Global",
    })
    found = _discover_rules(tmp_path)
    names = {p.name for p in found}
    assert "style.md" in names
    assert "react.mdc" in names
    assert "backend.md" in names
    assert "global.md" in names


def test_discover_commands_empty(tmp_path: Path) -> None:
    assert _discover_commands(tmp_path) == []


def test_discover_agents_empty(tmp_path: Path) -> None:
    assert _discover_agents(tmp_path) == []


def test_discover_rules_empty(tmp_path: Path) -> None:
    assert _discover_rules(tmp_path) == []
