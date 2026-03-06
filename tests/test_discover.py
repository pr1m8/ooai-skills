from __future__ import annotations
from pathlib import Path
from ooai_skills.discover import discover_skills
from ooai_skills.models import RepoSource
def test_discover(tmp_path: Path) -> None:
    root = tmp_path / 'r'
    d = root / 's' / 'a'
    d.mkdir(parents=True)
    (d / 'SKILL.md').write_text('---\nname: a\ndescription: b\n---\n', encoding='utf-8')
    skills, issues = discover_skills(root, RepoSource(repo='o/r'), commit_sha='c')
    assert len(skills) == 1
    assert all(i.severity != 'error' for i in issues)
