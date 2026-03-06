"""GitHub ZIP (archive) ingestion for :mod:`ooai_skills`.

Purpose:
    Support "no-git" ingestion by downloading GitHub repository archives (ZIP)
    and mirroring any discovered skill folders (directories containing ``SKILL.md``)
    into MinIO/S3.

Design:
    - Downloads ``https://github.com/<owner>/<repo>/archive/refs/heads/<ref>.zip``.
    - Extracts to a local working directory under ``work_dir``.
    - Discovers skills via :func:`~ooai_skills.discover.discover_skills`.
    - Uploads each skill directory to stable prefixes:
      ``packs/<owner>/<repo>/<skill_relpath>/...``.
    - Updates ``index/skills.json``, ``index/sources.json``, ``index/lint.json``.

Security:
    This module only downloads and uploads files; it does not execute any content.

Examples:
    ::
        >>> # doctest: +SKIP
        >>> # ooai-skills ingest-github-zip openai/skills --ref main
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from .discover import discover_skills
from .models import LintIndex, RepoSource, SkillIndex, SourceIndex
from .s3 import S3Client
from .settings import OoaiSkillsSettings

_INDEX_SKILLS = "index/skills.json"
_INDEX_SOURCES = "index/sources.json"
_INDEX_LINT = "index/lint.json"


@dataclass(frozen=True)
class GithubArchiveSpec:
    """A GitHub archive to download.

    Args:
        repo: ``owner/name``.
        ref: Branch/tag name or commit-ish.
        kind: One of ``heads`` or ``tags`` to construct the archive URL.

    Notes:
        GitHub's archive URL structure differs for heads vs tags.
    """

    repo: str
    ref: str = "main"
    kind: str = "heads"


def download_github_archive_zip(
    spec: GithubArchiveSpec,
    *,
    dest_zip: Path,
    token: str | None = None,
) -> Path:
    """Download a GitHub repo archive ZIP.

    Args:
        spec: GitHub archive spec.
        dest_zip: Destination zip path.
        token: Optional GitHub token to avoid rate limits.

    Returns:
        Path to the downloaded ZIP file.

    Raises:
        RuntimeError: If the download fails.

    Examples:
        ::
            >>> # doctest: +SKIP
            >>> from pathlib import Path
            >>> p = download_github_archive_zip(GithubArchiveSpec("openai/skills"), dest_zip=Path("x.zip"))
    """
    owner, name = spec.repo.split("/", 1)
    url = f"https://github.com/{owner}/{name}/archive/refs/{spec.kind}/{spec.ref}.zip"

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    dest_zip.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=headers, stream=True, timeout=120)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download {spec.repo}@{spec.ref}: HTTP {r.status_code}")

    with dest_zip.open("wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    return dest_zip


def extract_zip(zip_path: Path, dest_dir: Path) -> Path:
    """Extract a ZIP and return the inferred root folder.

    Args:
        zip_path: ZIP file path.
        dest_dir: Extraction directory.

    Returns:
        Root folder path (best-effort).

    Raises:
        FileNotFoundError: If ZIP doesn't exist.
        RuntimeError: If extraction fails.

    Examples:
        ::
            >>> # doctest: +SKIP
            >>> from pathlib import Path
            >>> extract_zip(Path("repo.zip"), Path("./out"))
    """
    if not zip_path.exists():
        raise FileNotFoundError(str(zip_path))

    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)

    # GitHub archives extract a single top-level directory typically.
    children = [p for p in dest_dir.iterdir() if p.is_dir()]
    if len(children) == 1:
        return children[0]
    return dest_dir


def ingest_github_archive_zip(
    repo: str,
    *,
    ref: str = "main",
    kind: str = "heads",
    settings: OoaiSkillsSettings,
    console: Console | None = None,
    token: str | None = None,
) -> None:
    """Download+ingest a GitHub archive ZIP into MinIO/S3.

    Args:
        repo: ``owner/name``.
        ref: Branch/tag name.
        kind: ``heads`` or ``tags``.
        settings: Settings.
        console: Optional Rich console.
        token: Optional GitHub token.

    Returns:
        None.

    Raises:
        RuntimeError: If download or upload fails.
    """
    con = console or Console()
    settings.work_dir.mkdir(parents=True, exist_ok=True)

    s3 = S3Client.from_settings(settings)

    existing_idx = s3.get_json(_INDEX_SKILLS) or {"skills": []}
    existing_hashes: dict[str, str] = {
        str(r.get("skill_id")): str(r.get("content_hash"))
        for r in existing_idx.get("skills", [])
        if isinstance(r, dict) and r.get("skill_id") and r.get("content_hash")
    }

    owner, name = repo.split("/", 1)
    zip_path = settings.work_dir / "archives" / owner / f"{name}__{kind}__{ref}.zip"
    extract_dir = settings.work_dir / "archives" / owner / f"{name}__{kind}__{ref}"

    spec = GithubArchiveSpec(repo=repo, ref=ref, kind=kind)
    con.print(f"Downloading GitHub archive: [cyan]{repo}@{ref}[/cyan]")
    download_github_archive_zip(spec, dest_zip=zip_path, token=token)
    root = extract_zip(zip_path, extract_dir)

    # Use commit marker as ref (archive doesn't reliably include commit).
    src = RepoSource(repo=repo, ref=ref)
    skills, issues = discover_skills(root, src, commit_sha=ref)

    lint_existing = s3.get_json(_INDEX_LINT) or {"issues": []}
    merged_lint = LintIndex.model_validate(lint_existing)
    merged_lint.issues.extend(issues)

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), TimeElapsedColumn(), console=con) as progress:
        task = progress.add_task(f"Uploading skills from {repo}...", total=len(skills))
        for sk in skills:
            # Ensure stable S3 prefix uses packs/<owner>/<repo>/...
            sk.s3_prefix = f"packs/{repo}/{sk.source_path}/".replace("//", "/")
            if existing_hashes.get(sk.skill_id) == sk.content_hash:
                progress.advance(task)
                continue
            s3.upload_dir(root / sk.source_path, sk.s3_prefix)
            progress.advance(task)

    merged = SkillIndex.model_validate(existing_idx)
    merged_map = {s.skill_id: s for s in merged.skills}
    for sk in skills:
        merged_map[sk.skill_id] = sk
    merged.skills = list(merged_map.values())

    src_existing = s3.get_json(_INDEX_SOURCES) or {"sources": {}}
    merged_src = SourceIndex.model_validate(src_existing)
    merged_src.sources[repo] = ref

    s3.put_json(_INDEX_SKILLS, merged.model_dump(mode="json"))
    s3.put_json(_INDEX_SOURCES, merged_src.model_dump(mode="json"))
    s3.put_json(_INDEX_LINT, merged_lint.model_dump(mode="json"))

    con.print(f"[green]Done.[/green] Ingested {len(skills)} skills from {repo}@{ref}.")
