"""Pull skills from MinIO to local cache + flattened view."""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .models import SkillIndex
from .s3 import S3Client
from .settings import OoaiSkillsSettings

_INDEX_SKILLS = "index/skills.json"


def pull_all(settings: OoaiSkillsSettings, *, console: Console | None = None, use_copy: bool = False) -> None:
    con = console or Console()
    s3 = S3Client.from_settings(settings)
    idx_raw = s3.get_json(_INDEX_SKILLS)
    if not idx_raw:
        raise RuntimeError(f"Missing index at '{_INDEX_SKILLS}'. Push/mirror first.")
    idx = SkillIndex.model_validate(idx_raw)

    packs = settings.local_packs_dir.expanduser()
    skills_dir = settings.local_skills_dir.expanduser()
    packs.mkdir(parents=True, exist_ok=True)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), TimeElapsedColumn(), console=con) as progress:
        task = progress.add_task("Downloading skills...", total=len(idx.skills))
        for sk in idx.skills:
            owner, repo = sk.source_repo.split("/", 1)
            local_skill_path = packs / owner / repo / sk.source_path
            s3.download_prefix(sk.s3_prefix, local_skill_path)
            progress.advance(task)

    rebuild_flat_view(idx, packs, skills_dir, console=con, use_copy=use_copy)


def rebuild_flat_view(idx: SkillIndex, packs_dir: Path, dest_dir: Path, *, console: Console | None = None, use_copy: bool = False) -> None:
    con = console or Console()
    dest_dir.mkdir(parents=True, exist_ok=True)

    for child in dest_dir.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)

    used: set[str] = set()
    for sk in idx.skills:
        owner, repo = sk.source_repo.split("/", 1)
        src = packs_dir / owner / repo / sk.source_path
        if not src.exists():
            continue
        name = _safe_name(sk.name or Path(sk.source_path).name, used, owner, repo)
        used.add(name)
        dst = dest_dir / name
        if use_copy:
            shutil.copytree(src, dst)
        else:
            _ensure_symlink(src, dst)

    con.print(f"[green]Flattened[/green] {len(used)} skills into {dest_dir}")


def _safe_name(base: str, used: set[str], owner: str, repo: str) -> str:
    candidate = base.strip().replace("/", "_") or "skill"
    if candidate not in used:
        return candidate
    candidate2 = f"{owner}__{repo}__{candidate}"
    if candidate2 not in used:
        return candidate2
    i = 2
    while f"{candidate2}__{i}" in used:
        i += 1
    return f"{candidate2}__{i}"


def _ensure_symlink(src: Path, dst: Path) -> None:
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    try:
        rel = os.path.relpath(src, start=dst.parent)
        dst.symlink_to(rel, target_is_directory=True)
    except Exception:
        dst.symlink_to(src, target_is_directory=True)
