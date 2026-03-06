"""Push local skills into MinIO."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .discover import discover_skills
from .models import LintIndex, RepoSource, SkillIndex, SourceIndex
from .s3 import S3Client
from .settings import OoaiSkillsSettings

_INDEX_SKILLS = "index/skills.json"
_INDEX_SOURCES = "index/sources.json"
_INDEX_LINT = "index/lint.json"


def push_local(source_dir: Path, *, pack: str, settings: OoaiSkillsSettings, console: Console | None = None) -> None:
    con = console or Console()
    if not source_dir.exists():
        raise FileNotFoundError(str(source_dir))

    s3 = S3Client.from_settings(settings)
    existing_idx = s3.get_json(_INDEX_SKILLS) or {"skills": []}
    existing_hashes = {
        str(r.get("skill_id")): str(r.get("content_hash"))
        for r in existing_idx.get("skills", [])
        if isinstance(r, dict) and r.get("skill_id") and r.get("content_hash")
    }

    source_repo = f"local/{pack}"
    src = RepoSource(repo=source_repo, ref="local")
    skills, issues = discover_skills(source_dir, src, commit_sha="local")

    for sk in skills:
        sk.s3_prefix = f"packs/local/{pack}/{sk.source_path}/".replace("//", "/")
        sk.source_repo = source_repo
        sk.source_commit = "local"

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), TimeElapsedColumn(), console=con) as progress:
        task = progress.add_task("Uploading local skills...", total=len(skills))
        for sk in skills:
            if existing_hashes.get(sk.skill_id) == sk.content_hash:
                progress.advance(task)
                continue
            s3.upload_dir(source_dir / sk.source_path, sk.s3_prefix)
            progress.advance(task)

    merged = SkillIndex.model_validate(existing_idx)
    merged_map = {s.skill_id: s for s in merged.skills}
    for sk in skills:
        merged_map[sk.skill_id] = sk
    merged.skills = list(merged_map.values())

    src_existing = s3.get_json(_INDEX_SOURCES) or {"sources": {}}
    merged_src = SourceIndex.model_validate(src_existing)
    merged_src.sources[source_repo] = "local"

    lint_existing = s3.get_json(_INDEX_LINT) or {"issues": []}
    merged_lint = LintIndex.model_validate(lint_existing)
    merged_lint.issues.extend(issues)

    s3.put_json(_INDEX_SKILLS, merged.model_dump(mode="json"))
    s3.put_json(_INDEX_SOURCES, merged_src.model_dump(mode="json"))
    s3.put_json(_INDEX_LINT, merged_lint.model_dump(mode="json"))

    con.print(f"[green]Done.[/green] Uploaded {len(skills)} skills from {source_dir}")
