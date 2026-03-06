"""Local browsing of downloaded skills."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .frontmatter import parse_frontmatter


@dataclass(frozen=True)
class LocalSkill:
    dir_path: Path
    folder_name: str
    name: str
    description: str


def iter_local_skills(root: Path) -> Iterable[LocalSkill]:
    if not root.exists():
        raise FileNotFoundError(str(root))
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if not skill_md.exists():
            continue
        md = skill_md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(md)["frontmatter"]
        name = str(fm.get("name") or child.name).strip() or child.name
        desc = str(fm.get("description") or "").strip()
        yield LocalSkill(child, child.name, name, desc)


def find_local_skills(root: Path, pattern: str) -> list[LocalSkill]:
    p = pattern.strip().lower()
    return [sk for sk in iter_local_skills(root) if p in f"{sk.name}
{sk.description}
{sk.folder_name}".lower()]


def resolve_local_skill(root: Path, query: str) -> LocalSkill | None:
    q = query.strip().lower()
    fallback = None
    for sk in iter_local_skills(root):
        if sk.folder_name.lower() == q or sk.name.lower() == q:
            return sk
        if fallback is None and (q in sk.name.lower() or q in sk.folder_name.lower()):
            fallback = sk
    return fallback
