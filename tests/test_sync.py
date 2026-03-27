from __future__ import annotations

from pathlib import Path

from ooai_skills.models import SkillIndex, SkillRecord
from ooai_skills.sync import rebuild_flat_view


def _make_skill(tmp: Path, name: str) -> tuple[SkillRecord, Path]:
    """Create a skill directory and return (record, pack_path)."""
    pack = tmp / "packs" / "owner" / "repo" / name
    pack.mkdir(parents=True)
    (pack / "SKILL.md").write_text(f"---\nname: {name}\ndescription: test\n---\n", encoding="utf-8")
    return SkillRecord(
        skill_id=f"owner/repo::{name}",
        name=name,
        source_repo="owner/repo",
        source_commit="abc",
        source_path=name,
        content_hash="hash1",
        s3_prefix=f"packs/owner/repo/{name}/",
    ), pack


def test_rebuild_flat_view(tmp_path: Path) -> None:
    """Test basic flattening with symlinks."""
    rec, _ = _make_skill(tmp_path, "skill-a")
    idx = SkillIndex(skills=[rec])
    dest = tmp_path / "flat"

    rebuild_flat_view(idx, tmp_path / "packs" / "owner" / "repo" / ".." / ".." / ".." / "packs", dest)
    # Simpler: just use correct packs_dir
    dest2 = tmp_path / "flat2"
    packs_dir = tmp_path / "packs"
    rebuild_flat_view(idx, packs_dir, dest2)

    assert (dest2 / "skill-a").exists() or (dest2 / "skill-a").is_symlink()
    assert (dest2 / "skill-a" / "SKILL.md").exists()


def test_rebuild_flat_view_copy(tmp_path: Path) -> None:
    """Test flattening with copies instead of symlinks."""
    rec, _ = _make_skill(tmp_path, "skill-b")
    idx = SkillIndex(skills=[rec])
    dest = tmp_path / "flat"
    packs_dir = tmp_path / "packs"

    rebuild_flat_view(idx, packs_dir, dest, use_copy=True)

    assert (dest / "skill-b").is_dir()
    assert not (dest / "skill-b").is_symlink()
    assert (dest / "skill-b" / "SKILL.md").exists()


def test_multi_target(tmp_path: Path) -> None:
    """Verify rebuild_flat_view works on multiple target dirs independently."""
    rec, _ = _make_skill(tmp_path, "skill-c")
    idx = SkillIndex(skills=[rec])
    packs_dir = tmp_path / "packs"

    target1 = tmp_path / "target1"
    target2 = tmp_path / "target2"

    rebuild_flat_view(idx, packs_dir, target1)
    rebuild_flat_view(idx, packs_dir, target2)

    assert (target1 / "skill-c" / "SKILL.md").exists()
    assert (target2 / "skill-c" / "SKILL.md").exists()


def test_name_collision(tmp_path: Path) -> None:
    """Two skills with the same name get unique flat names."""
    pack1 = tmp_path / "packs" / "org1" / "repo1" / "skill"
    pack1.mkdir(parents=True)
    (pack1 / "SKILL.md").write_text("---\nname: skill\n---\n", encoding="utf-8")
    r1 = SkillRecord(
        skill_id="org1/repo1::skill", name="skill",
        source_repo="org1/repo1", source_commit="a", source_path="skill",
        content_hash="h1", s3_prefix="packs/org1/repo1/skill/",
    )

    pack2 = tmp_path / "packs" / "org2" / "repo2" / "skill"
    pack2.mkdir(parents=True)
    (pack2 / "SKILL.md").write_text("---\nname: skill\n---\n", encoding="utf-8")
    r2 = SkillRecord(
        skill_id="org2/repo2::skill", name="skill",
        source_repo="org2/repo2", source_commit="b", source_path="skill",
        content_hash="h2", s3_prefix="packs/org2/repo2/skill/",
    )

    idx = SkillIndex(skills=[r1, r2])
    dest = tmp_path / "flat"
    packs_dir = tmp_path / "packs"

    rebuild_flat_view(idx, packs_dir, dest)

    children = sorted(p.name for p in dest.iterdir())
    assert len(children) == 2
    assert "skill" in children
