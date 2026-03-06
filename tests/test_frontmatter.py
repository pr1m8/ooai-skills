from __future__ import annotations
from ooai_skills.frontmatter import parse_frontmatter
def test_fm() -> None:
    got = parse_frontmatter('---\nname: x\n---\n# hi\n')
    assert got['frontmatter']['name'] == 'x'
