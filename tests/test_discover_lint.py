"""Tests for the enhanced linting rules (TK001, EXT001)."""
from __future__ import annotations

from pathlib import Path

from ooai_skills.discover import discover_skills
from ooai_skills.models import RepoSource


def test_tk001_token_budget(tmp_path: Path) -> None:
    """TK001: warn when SKILL.md body exceeds ~5000 tokens."""
    root = tmp_path / "repo"
    skill = root / "big-skill"
    skill.mkdir(parents=True)
    # ~5000 tokens ≈ ~20000 chars; write 25000 to trigger
    (skill / "SKILL.md").write_text(
        "---\nname: big-skill\ndescription: test\n---\n" + "x" * 25000,
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "TK001" in codes


def test_ext001_unknown_frontmatter(tmp_path: Path) -> None:
    """EXT001: warn on unknown frontmatter keys."""
    root = tmp_path / "repo"
    skill = root / "weird-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: weird\ndescription: test\ncustom_field: bad\nfoo: bar\n---\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "EXT001" in codes
    ext_issue = next(i for i in issues if i.code == "EXT001")
    assert "custom_field" in ext_issue.message
    assert "foo" in ext_issue.message


def test_known_claude_extensions_pass(tmp_path: Path) -> None:
    """Claude Code extension keys should NOT trigger EXT001."""
    root = tmp_path / "repo"
    skill = root / "good-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: good\ndescription: test\ncontext: fork\nagent: Explore\n"
        "effort: high\nmodel: claude-opus-4-6\npaths:\n  - '**/*.py'\n---\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "EXT001" not in codes


def test_no_warnings_for_clean_skill(tmp_path: Path) -> None:
    """A well-formed, small skill should produce no warnings."""
    root = tmp_path / "repo"
    skill = root / "clean"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: clean\ndescription: A clean skill.\n---\n# Clean\nDo the thing.\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    assert len(issues) == 0


def test_nm001_name_format(tmp_path: Path) -> None:
    """NM001: warn when name has invalid format."""
    root = tmp_path / "repo"
    skill = root / "bad"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: Bad_Name Here\ndescription: test\n---\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "NM001" in codes


def test_nm002_name_dir_mismatch(tmp_path: Path) -> None:
    """NM002: warn when name doesn't match directory."""
    root = tmp_path / "repo"
    skill = root / "actual-dir"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: different-name\ndescription: test\n---\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "NM002" in codes


def test_desc001_description_too_long(tmp_path: Path) -> None:
    """DESC001: warn when description exceeds 1024 chars."""
    root = tmp_path / "repo"
    skill = root / "verbose"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: verbose\ndescription: {'x' * 1100}\n---\n",
        encoding="utf-8",
    )
    _, issues = discover_skills(root, RepoSource(repo="o/r"), commit_sha="c")
    codes = [i.code for i in issues]
    assert "DESC001" in codes
