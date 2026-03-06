"""ooai_skills package.

Purpose:
    A tiny MinIO/S3-backed registry for Agent Skills (folders containing ``SKILL.md``),
    plus a local CLI that can pull skills into Deep Agents-compatible directories
    and browse them.

Design:
    - Skill discovery is file-based: any directory containing ``SKILL.md`` is a skill.
    - Skills are stored in MinIO under stable prefixes and indexed via JSON.
    - Pulling builds:
        - ``~/.agents/skillpacks``: cached content
        - ``~/.agents/skills``: flattened view (symlinks by default)

Examples:
    ::
        >>> from ooai_skills.settings import OoaiSkillsSettings
        >>> OoaiSkillsSettings().bucket
        'agent-skills'
"""

from __future__ import annotations

from .models import CuratedRepo, LintIssue, RepoSource, SkillIndex, SkillRecord, SourceIndex
from .settings import OoaiSkillsSettings

__all__ = [
    "CuratedRepo",
    "LintIssue",
    "OoaiSkillsSettings",
    "RepoSource",
    "SkillIndex",
    "SkillRecord",
    "SourceIndex",
]
