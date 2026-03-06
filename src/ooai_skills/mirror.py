from __future__ import annotations
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from .discover import discover_skills
from .models import LintIndex, RepoSource, SkillIndex, SourceIndex
from .s3 import S3Client
from .settings import OoaiSkillsSettings
from .git import clone_repo

_INDEX_SKILLS='index/skills.json'
_INDEX_SOURCES='index/sources.json'
_INDEX_LINT='index/lint.json'

def mirror_sources(sources: list[RepoSource], settings: OoaiSkillsSettings, *, console: Console | None=None) -> None:
    con = console or Console()
    settings.work_dir.mkdir(parents=True, exist_ok=True)
    s3 = S3Client.from_settings(settings)
    existing = s3.get_json(_INDEX_SKILLS) or {'skills': []}
    existing_hashes = {str(r.get('skill_id')): str(r.get('content_hash')) for r in existing.get('skills', []) if isinstance(r, dict)}
    found = SkillIndex()
    src_index = SourceIndex(meta={'tool':'ooai-skills'})
    lint = LintIndex()
    with Progress(SpinnerColumn(), TextColumn('{task.description}'), TimeElapsedColumn(), console=con) as progress:
        task = progress.add_task('Mirroring repos...', total=len(sources))
        for src in sources:
            owner, name = src.repo.split('/',1)
            repo_dir = settings.work_dir / 'repos' / owner / name
            progress.update(task, description=f'Fetch {src.repo}@{src.ref}')
            sha = clone_repo(src.repo, src.ref, repo_dir)
            src_index.sources[src.repo] = sha
            skills, issues = discover_skills(repo_dir, src, commit_sha=sha)
            lint.issues.extend(issues)
            for sk in skills:
                if existing_hashes.get(sk.skill_id) == sk.content_hash:
                    continue
                s3.upload_dir(repo_dir / sk.source_path, sk.s3_prefix)
            found.skills.extend(skills)
            progress.advance(task)
    merged = SkillIndex.model_validate(existing)
    m = {s.skill_id: s for s in merged.skills}
    for sk in found.skills:
        m[sk.skill_id] = sk
    merged.skills = list(m.values())
    src_existing = s3.get_json(_INDEX_SOURCES) or {'sources': {}}
    merged_src = SourceIndex.model_validate(src_existing)
    merged_src.sources.update(src_index.sources)
    lint_existing = s3.get_json(_INDEX_LINT) or {'issues': []}
    merged_lint = LintIndex.model_validate(lint_existing)
    merged_lint.issues.extend(lint.issues)
    s3.put_json(_INDEX_SKILLS, merged.model_dump(mode='json'))
    s3.put_json(_INDEX_SOURCES, merged_src.model_dump(mode='json'))
    s3.put_json(_INDEX_LINT, merged_lint.model_dump(mode='json'))
    con.print(f'[green]Done[/green]: mirrored {len(found.skills)} skills.')
