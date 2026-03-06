from __future__ import annotations
from pathlib import Path
from typing import Annotated
import typer
from rich.console import Console
from rich.table import Table

from .curated import all_repos, categories as curated_categories, filter_repos
from .local import find_local_skills, iter_local_skills, resolve_local_skill
from .mirror import mirror_sources
from .models import RepoSource
from .push_local import push_local
from .settings import OoaiSkillsSettings
from .sources import load_sources_file
from .sync import pull_all

app = typer.Typer(add_completion=False, help='ooai-skills: MinIO registry + Git mirroring + local browse.')
cur = typer.Typer(help='Curated repo list (embedded).')
loc = typer.Typer(help='Browse local skills (from ~/.agents/skills).')
app.add_typer(cur, name='curated')
app.add_typer(loc, name='local')

@app.command('push-local')
def cmd_push_local(source_dir: Annotated[Path, typer.Argument()], pack: Annotated[str, typer.Option('--pack')]='manual') -> None:
    push_local(source_dir.expanduser(), pack=pack, settings=OoaiSkillsSettings(), console=Console())

@app.command('pull')
def cmd_pull(all_: Annotated[bool, typer.Option('--all')]=True, copy: Annotated[bool, typer.Option('--copy')]=False) -> None:
    if not all_:
        raise typer.Exit(code=2)
    pull_all(OoaiSkillsSettings(), console=Console(), use_copy=copy)

@app.command('mirror')
def cmd_mirror(sources_file: Annotated[Path, typer.Argument()]) -> None:
    sources = load_sources_file(sources_file)
    mirror_sources(sources, OoaiSkillsSettings(), console=Console())

@app.command('mirror-curated')
def cmd_mirror_curated(category: Annotated[list[str], typer.Option('--category')]=[], kinds: Annotated[list[str], typer.Option('--kinds')]=['skills']) -> None:
    use_kinds = set(kinds)
    allowed = set(category) if category else None
    repos = all_repos()
    if allowed is not None:
        repos = [r for r in repos if r.category in allowed]
    repos = [r for r in repos if r.kind in use_kinds]
    mirror_sources([RepoSource(repo=r.repo, ref='main') for r in repos], OoaiSkillsSettings(), console=Console())

@cur.command('categories')
def cmd_cur_categories() -> None:
    con = Console()
    table = Table(title='Curated categories')
    table.add_column('Category', style='bold')
    table.add_column('Repos', justify='right')
    for c in curated_categories():
        table.add_row(c, str(len(filter_repos(category=c))))
    con.print(table)

@cur.command('list')
def cmd_cur_list(category: Annotated[str | None, typer.Option('--category')]=None, kind: Annotated[list[str], typer.Option('--kind')]=[], limit: Annotated[int, typer.Option('--limit')]=200) -> None:
    kinds = set(kind) if kind else None
    repos = filter_repos(category=category, kinds=kinds)
    con = Console()
    table = Table(title=f'Curated repos ({len(repos)})')
    table.add_column('Category')
    table.add_column('Kind')
    table.add_column('Repo', style='cyan')
    table.add_column('Description')
    for r in repos[:limit]:
        table.add_row(r.category, r.kind, r.repo, r.description)
    con.print(table)

@cur.command('export')
def cmd_cur_export(out_path: Annotated[Path, typer.Argument()], kinds: Annotated[list[str], typer.Option('--kinds')]=['skills'], all_categories: Annotated[bool, typer.Option('--all-categories')]=True, category: Annotated[list[str], typer.Option('--category')]=[]) -> None:
    use_kinds = set(kinds)
    repos = [r for r in all_repos() if r.kind in use_kinds]
    if not all_categories:
        allowed = set(category)
        repos = [r for r in repos if r.category in allowed]
    lines = ['sources:']
    for r in repos:
        lines.append(f'  - repo: {r.repo}')
        lines.append('    ref: main')
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    Console().print(f'[green]Wrote[/green] {out_path} with {len(repos)} repos.')

@loc.command('list')
def cmd_loc_list(root: Annotated[Path | None, typer.Option('--root')]=None, limit: Annotated[int, typer.Option('--limit')]=200) -> None:
    settings = OoaiSkillsSettings()
    skills_root = (root or settings.local_skills_dir).expanduser()
    rows = list(iter_local_skills(skills_root))
    con = Console()
    table = Table(title=f'Local skills in {skills_root} ({min(limit,len(rows))}/{len(rows)})')
    table.add_column('Folder', style='cyan', no_wrap=True)
    table.add_column('Name', style='bold')
    table.add_column('Description')
    for sk in rows[:limit]:
        table.add_row(sk.folder_name, sk.name, sk.description[:120])
    con.print(table)

@loc.command('find')
def cmd_loc_find(pattern: Annotated[str, typer.Argument()], root: Annotated[Path | None, typer.Option('--root')]=None, limit: Annotated[int, typer.Option('--limit')]=50) -> None:
    settings = OoaiSkillsSettings()
    skills_root = (root or settings.local_skills_dir).expanduser()
    hits = find_local_skills(skills_root, pattern)
    con = Console()
    table = Table(title=f"Local find '{pattern}' ({min(limit,len(hits))}/{len(hits)})")
    table.add_column('Folder', style='cyan', no_wrap=True)
    table.add_column('Name', style='bold')
    table.add_column('Description')
    for sk in hits[:limit]:
        table.add_row(sk.folder_name, sk.name, sk.description[:120])
    con.print(table)

@loc.command('info')
def cmd_loc_info(name: Annotated[str, typer.Argument()], root: Annotated[Path | None, typer.Option('--root')]=None) -> None:
    settings = OoaiSkillsSettings()
    skills_root = (root or settings.local_skills_dir).expanduser()
    sk = resolve_local_skill(skills_root, name)
    con = Console()
    if not sk:
        con.print(f'[red]Not found[/red]: {name}')
        raise typer.Exit(code=1)
    con.print(f'[bold]{sk.name}[/bold]\nFolder: {sk.folder_name}\nPath: {sk.dir_path}')

@loc.command('cat')
def cmd_loc_cat(name: Annotated[str, typer.Argument()], root: Annotated[Path | None, typer.Option('--root')]=None, head: Annotated[int, typer.Option('--head')]=120) -> None:
    settings = OoaiSkillsSettings()
    skills_root = (root or settings.local_skills_dir).expanduser()
    sk = resolve_local_skill(skills_root, name)
    con = Console()
    if not sk:
        con.print(f'[red]Not found[/red]: {name}')
        raise typer.Exit(code=1)
    p = sk.dir_path / 'SKILL.md'
    lines = p.read_text(encoding='utf-8', errors='replace').splitlines()
    if head > 0:
        lines = lines[:head]
    con.print('\n'.join(lines))


remote = typer.Typer(help='Remote helpers.')
app.add_typer(remote, name='remote')

@remote.command('stats')
def cmd_remote_stats() -> None:
    from .remote_tools import remote_stats
    remote_stats(OoaiSkillsSettings(), console=Console())


# --- ZIP ingestion (no-git) ---

@app.command('ingest-github-zip')
def cmd_ingest_github_zip(
    repo: str,
    ref: str = typer.Option('main', '--ref', help='Branch/tag name.'),
    kind: str = typer.Option('heads', '--kind', help="Archive kind: 'heads' or 'tags'."),
    github_token: str | None = typer.Option(None, '--github-token', help='Optional GitHub token.'),
) -> None:
    """Ingest a GitHub repo by downloading its archive ZIP (no git)."""
    from .ingest_zip import ingest_github_archive_zip
    ingest_github_archive_zip(
        repo,
        ref=ref,
        kind=kind,
        settings=OoaiSkillsSettings(),
        console=Console(),
        token=github_token,
    )

@app.command('ingest-curated-zips')
def cmd_ingest_curated_zips(
    category: list[str] = typer.Option([], '--category', help='Category to include (repeatable).'),
    kinds: list[str] = typer.Option(['skills'], '--kinds', help='Kinds to include (repeatable).'),
    ref: str = typer.Option('main', '--ref', help='Branch/tag for all repos.'),
    kind: str = typer.Option('heads', '--kind', help="Archive kind: 'heads' or 'tags'."),
    github_token: str | None = typer.Option(None, '--github-token', help='Optional GitHub token.'),
) -> None:
    """Ingest curated repos by downloading GitHub archive ZIPs (no git)."""
    from .curated import all_repos
    from .ingest_zip import ingest_github_archive_zip

    use_kinds = set(kinds)
    allowed = set(category) if category else None

    repos = all_repos()
    if allowed is not None:
        repos = [r for r in repos if r.category in allowed]
    repos = [r for r in repos if r.kind in use_kinds]

    con = Console()
    con.print(f'Ingesting {len(repos)} repos via ZIP archives...')
    for r in repos:
        ingest_github_archive_zip(
            r.repo,
            ref=ref,
            kind=kind,
            settings=OoaiSkillsSettings(),
            console=con,
            token=github_token,
        )
