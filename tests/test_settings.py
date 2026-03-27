from __future__ import annotations

import os

from ooai_skills.settings import OoaiSkillsSettings


def test_defaults() -> None:
    s = OoaiSkillsSettings()
    assert s.local_skills_dir.as_posix().endswith("/.agents/skills")
    assert s.local_packs_dir.as_posix().endswith("/.agents/skillpacks")
    assert s.bucket == "agent-skills"


def test_extra_targets_default() -> None:
    s = OoaiSkillsSettings()
    resolved = s.resolved_extra_targets
    assert len(resolved) >= 1
    assert any(str(p).endswith(".claude/skills") for p in resolved)


def test_extra_targets_parse_comma() -> None:
    os.environ["OOAI_SKILLS_EXTRA_TARGETS"] = "/tmp/a,/tmp/b"
    try:
        s = OoaiSkillsSettings()
        assert s.extra_targets_list == ["/tmp/a", "/tmp/b"]
        assert len(s.resolved_extra_targets) == 2
    finally:
        os.environ.pop("OOAI_SKILLS_EXTRA_TARGETS", None)


def test_extra_targets_empty_string() -> None:
    os.environ["OOAI_SKILLS_EXTRA_TARGETS"] = ""
    try:
        s = OoaiSkillsSettings()
        assert s.extra_targets_list == []
        assert s.resolved_extra_targets == []
    finally:
        os.environ.pop("OOAI_SKILLS_EXTRA_TARGETS", None)


def test_extra_targets_single() -> None:
    os.environ["OOAI_SKILLS_EXTRA_TARGETS"] = "~/.claude/skills"
    try:
        s = OoaiSkillsSettings()
        assert len(s.extra_targets_list) == 1
        assert s.resolved_extra_targets[0].as_posix().endswith(".claude/skills")
    finally:
        os.environ.pop("OOAI_SKILLS_EXTRA_TARGETS", None)
