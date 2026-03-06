"""Discover skills by locating **/SKILL.md."""

from __future__ import annotations

import fnmatch
from pathlib import Path
from typing import Any

from .frontmatter import parse_frontmatter
from .hashing import hash_dir
from .models import LintIssue, RepoSource, SkillRecord


def discover_skills(repo_root: Path, source: RepoSource, commit_sha: str) -> tuple[list[SkillRecord], list[LintIssue]]:
    if not repo_root.exists():
        raise FileNotFoundError(str(repo_root))

    skills: list[SkillRecord] = []
    issues: list[LintIssue] = []

    for skill_md in sorted(repo_root.rglob("SKILL.md")):
        skill_dir = skill_md.parent
        rel_dir = skill_dir.relative_to(repo_root).as_posix()

        if not _match_globs(rel_dir, source.include_globs, source.exclude_globs):
            continue

        md_text = skill_md.read_text(encoding="utf-8", errors="replace")
        parsed = parse_frontmatter(md_text)
        fm: dict[str, Any] = parsed["frontmatter"]

        name = str(fm.get("name") or skill_dir.name).strip() or skill_dir.name
        desc = str(fm.get("description") or "").strip()

        skill_id = f"{source.repo}::{rel_dir}"
        s3_prefix = f"packs/{source.repo}/{rel_dir}/".replace("//", "/")
        content_hash = hash_dir(skill_dir)

        skills.append(
            SkillRecord(
                skill_id=skill_id,
                name=name,
                description=desc,
                source_repo=source.repo,
                source_commit=commit_sha,
                source_path=rel_dir,
                content_hash=content_hash,
                s3_prefix=s3_prefix,
                frontmatter=fm,
            )
        )
        issues.extend(_lint(skill_id, skill_md, fm))

    return skills, issues


def _match_globs(rel_dir: str, include: list[str], exclude: list[str]) -> bool:
    if include and not any(fnmatch.fnmatch(rel_dir, pat) for pat in include):
        return False
    if exclude and any(fnmatch.fnmatch(rel_dir, pat) for pat in exclude):
        return False
    return True


def _lint(skill_id: str, skill_md: Path, fm: dict[str, Any]) -> list[LintIssue]:
    out: list[LintIssue] = []
    if "name" not in fm:
        out.append(LintIssue(skill_id=skill_id, severity="warning", code="FM001", message="Missing frontmatter name.", path="SKILL.md"))
    if "description" not in fm:
        out.append(LintIssue(skill_id=skill_id, severity="warning", code="FM002", message="Missing frontmatter description.", path="SKILL.md"))
    if skill_md.stat().st_size > 10 * 1024 * 1024:
        out.append(LintIssue(skill_id=skill_id, severity="error", code="SZ001", message="SKILL.md exceeds 10MB.", path="SKILL.md"))
    return out
