"""Discover skills by locating ``SKILL.md`` files recursively."""

from __future__ import annotations

import fnmatch
import re
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


_KNOWN_FRONTMATTER_KEYS = {
    # Base SKILL.md standard (agentskills.io)
    "name", "description", "license", "compatibility", "metadata", "allowed-tools",
    # Claude Code extensions
    "disable-model-invocation", "user-invocable", "context", "agent", "effort",
    "model", "shell", "hooks", "argument-hint", "paths",
}

_TOKEN_BUDGET = 5000
_APPROX_CHARS_PER_TOKEN = 4
_NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$")


def _lint(skill_id: str, skill_md: Path, fm: dict[str, Any]) -> list[LintIssue]:
    out: list[LintIssue] = []
    skill_dir = skill_md.parent
    name = str(fm.get("name", "")).strip()
    desc = str(fm.get("description", "")).strip()

    # FM001/FM002: missing fields
    if not name:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="FM001",
            message="Missing frontmatter name.", path="SKILL.md",
        ))
    if "description" not in fm:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="FM002",
            message="Missing frontmatter description.", path="SKILL.md",
        ))

    # SZ001: file size
    file_size = skill_md.stat().st_size
    if file_size > 10 * 1024 * 1024:
        out.append(LintIssue(
            skill_id=skill_id, severity="error", code="SZ001",
            message="SKILL.md exceeds 10MB.", path="SKILL.md",
        ))

    # TK001: body exceeds recommended token budget
    approx_tokens = file_size // _APPROX_CHARS_PER_TOKEN
    if approx_tokens > _TOKEN_BUDGET:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="TK001",
            message=f"SKILL.md body ~{approx_tokens} tokens exceeds {_TOKEN_BUDGET} recommended.",
            path="SKILL.md",
        ))

    # EXT001: unknown frontmatter keys
    unknown = set(fm.keys()) - _KNOWN_FRONTMATTER_KEYS
    if unknown:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="EXT001",
            message=f"Unknown frontmatter keys: {', '.join(sorted(unknown))}",
            path="SKILL.md",
        ))

    # NM001: name format (1-64 chars, lowercase + hyphens)
    if name and not _NAME_RE.match(name):
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="NM001",
            message=f"Name '{name}' must be 1-64 chars, lowercase alphanumeric + hyphens.",
            path="SKILL.md",
        ))

    # NM002: name must match directory name
    if name and name != skill_dir.name:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="NM002",
            message=f"Name '{name}' does not match directory '{skill_dir.name}'.",
            path="SKILL.md",
        ))

    # DESC001: description length
    if desc and len(desc) > 1024:
        out.append(LintIssue(
            skill_id=skill_id, severity="warning", code="DESC001",
            message=f"Description is {len(desc)} chars, exceeds 1024 max.",
            path="SKILL.md",
        ))

    return out
