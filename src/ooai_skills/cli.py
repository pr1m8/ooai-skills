from __future__ import annotations

import shutil
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

@app.command('init')
def cmd_init(
    project_dir: Annotated[Path, typer.Argument(help='Project root to scaffold.')] = Path('.'),
    no_mcp: Annotated[bool, typer.Option('--no-mcp', help='Skip .mcp.json creation.')] = False,
    no_claude_md: Annotated[bool, typer.Option('--no-claude-md', help='Skip CLAUDE.md changes.')] = False,
    no_agents_md: Annotated[bool, typer.Option('--no-agents-md', help='Skip AGENTS.md creation.')] = False,
) -> None:
    """Scaffold multi-agent directory structure (Claude Code, Deep Agents, Codex, Gemini, Cursor, Copilot)."""
    from .init import init_project
    init_project(
        project_dir.expanduser().resolve(),
        console=Console(),
        with_mcp=not no_mcp,
        with_claude_md=not no_claude_md,
        with_agents_md=not no_agents_md,
    )


@app.command('create')
def cmd_create(
    name: Annotated[str, typer.Argument(help='Name (lowercase, hyphens ok).')],
    kind: Annotated[str, typer.Option('--kind', help='What to create: skill, command, agent, rule.')] = 'skill',
    target: Annotated[str, typer.Option('--target', help='Where to create: claude, agents, or both.')] = 'both',
) -> None:
    """Create a new skill, command, agent, or rule from template."""
    import re
    con = Console()
    if not re.match(r"^[a-z0-9]([a-z0-9-]{0,62}[a-z0-9])?$", name):
        con.print(f"[red]Invalid name:[/red] '{name}' — must be 1-64 chars, lowercase alphanumeric + hyphens.")
        raise typer.Exit(code=1)

    created: list[str] = []

    if kind == "skill":
        template = (
            f"---\nname: {name}\ndescription: TODO — describe what this skill does "
            f"and when to use it.\n---\n\n# {name}\n\nTODO: Add instructions here.\n"
        )
        paths: list[Path] = []
        if target in ("claude", "both"):
            paths.append(Path(".claude/skills") / name / "SKILL.md")
        if target in ("agents", "both"):
            paths.append(Path(".agents/skills") / name / "SKILL.md")
        for p in paths:
            if p.exists():
                con.print(f"[yellow]Already exists:[/yellow] {p}")
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(template, encoding="utf-8")
            created.append(str(p))

    elif kind == "command":
        template = (
            f"# {name}\n\nTODO: Add command instructions here.\n\n$ARGUMENTS\n"
        )
        p = Path(".claude/commands") / f"{name}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.write_text(template, encoding="utf-8")
            created.append(str(p))
        else:
            con.print(f"[yellow]Already exists:[/yellow] {p}")

    elif kind == "agent":
        template = (
            f"---\nname: {name}\ndescription: TODO — describe what this agent specializes in.\n"
            f"model: claude-sonnet-4-6\n---\n\n# {name}\n\nTODO: Add agent instructions.\n"
        )
        paths_agent: list[Path] = [
            Path(".claude/agents") / f"{name}.md",
            Path(".agents/personas") / f"{name}.md",
        ]
        for p in paths_agent:
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text(template, encoding="utf-8")
                created.append(str(p))

    elif kind == "rule":
        template = (
            f"---\nglobs: \"**/*\"\n---\n\n# {name}\n\nTODO: Add rule content.\n"
        )
        paths_rule: list[Path] = []
        if target in ("claude", "both"):
            paths_rule.append(Path(".claude/rules") / f"{name}.md")
        if target in ("agents", "both"):
            paths_rule.append(Path(".agents/rules") / f"{name}.md")
        for p in paths_rule:
            p.parent.mkdir(parents=True, exist_ok=True)
            if not p.exists():
                p.write_text(template, encoding="utf-8")
                created.append(str(p))

    else:
        con.print(f"[red]Unknown kind:[/red] {kind}. Use: skill, command, agent, rule.")
        raise typer.Exit(code=1)

    for c in created:
        con.print(f"  [green]+[/green] {c}")
    if created:
        con.print(f"\n[green]Created {kind}[/green] '{name}'.")
    else:
        con.print("[dim]Nothing to create (all files already exist).[/dim]")


@app.command('status')
def cmd_status() -> None:
    """Show skill installation status across all targets."""
    settings = OoaiSkillsSettings()
    con = Console()
    table = Table(title="Skill Installation Status")
    table.add_column("Location", style="cyan")
    table.add_column("Skills", justify="right", style="bold")
    table.add_column("Path")

    locations = [
        ("Primary", settings.local_skills_dir.expanduser()),
    ]
    for extra in settings.resolved_extra_targets:
        locations.append(("Extra target", extra))

    # Also check project-local dirs
    for label, rel in [
        ("Project .claude", Path(".claude/skills")),
        ("Project .agents", Path(".agents/skills")),
    ]:
        if rel.exists():
            locations.append((label, rel.resolve()))

    for label, path in locations:
        if path.exists():
            count = sum(1 for c in path.iterdir() if c.is_dir() and (c / "SKILL.md").exists())
            table.add_row(label, str(count), str(path))
        else:
            table.add_row(label, "-", f"{path} [dim](not found)[/dim]")

    con.print(table)


@app.command('install')
def cmd_install(
    source: Annotated[str, typer.Argument(help='GitHub repo (owner/repo) or URL.')],
    ref: Annotated[str, typer.Option('--ref', help='Branch or tag.')] = 'main',
    what: Annotated[str, typer.Option('--what', help="What to install: all, skills, commands, agents, rules.")] = 'all',
    name: Annotated[str | None, typer.Option('--name', help='Only install items matching this name.')] = None,
) -> None:
    """Install skills/commands/agents/rules directly from GitHub (no MinIO)."""
    from .direct import install_from_url
    install_from_url(source, what=what, settings=OoaiSkillsSettings(), console=Console())


@app.command('push-local')
def cmd_push_local(source_dir: Annotated[Path, typer.Argument()], pack: Annotated[str, typer.Option('--pack')]='manual') -> None:
    push_local(source_dir.expanduser(), pack=pack, settings=OoaiSkillsSettings(), console=Console())

@app.command('pull')
def cmd_pull(
    all_: Annotated[bool, typer.Option('--all')] = True,
    copy: Annotated[bool, typer.Option('--copy')] = False,
    target: Annotated[list[Path], typer.Option('--target', help='Additional output dirs (repeatable).')] = [],
    no_extra: Annotated[bool, typer.Option('--no-extra', help='Skip default extra targets (e.g. ~/.claude/skills).')] = False,
    name: Annotated[str | None, typer.Option('--name', help='Pull a single skill by name from registry.')] = None,
    category: Annotated[str | None, typer.Option('--category', help='Only pull skills from repos in this curated category.')] = None,
) -> None:
    """Pull skills from MinIO registry to local directories."""
    from .sync import pull_single
    settings = OoaiSkillsSettings()
    if no_extra:
        settings.extra_targets = ""
    if target:
        settings.extra_targets = ",".join(str(t.expanduser()) for t in target)

    con = Console()

    # Single skill by name
    if name:
        if not pull_single(name, settings, console=con, use_copy=copy):
            raise typer.Exit(code=1)
        return

    # Selective pull by category
    skill_filter = None
    if category:
        cat_repos = {r.repo for r in filter_repos(category=category)}
        skill_filter = lambda sk: sk.source_repo in cat_repos  # noqa: E731

    pull_all(settings, console=con, use_copy=copy, skill_filter=skill_filter)

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

@loc.command('remove')
def cmd_loc_remove(
    name: Annotated[str, typer.Argument(help='Skill name or folder to remove.')],
    root: Annotated[Path | None, typer.Option('--root')] = None,
    all_targets: Annotated[bool, typer.Option('--all-targets', help='Also remove from extra targets (e.g. ~/.claude/skills).')] = False,
) -> None:
    """Remove a locally installed skill."""
    settings = OoaiSkillsSettings()
    con = Console()
    removed = 0

    roots = [(root or settings.local_skills_dir).expanduser()]
    if all_targets:
        roots.extend(settings.resolved_extra_targets)

    for skills_root in roots:
        sk = resolve_local_skill(skills_root, name) if skills_root.exists() else None
        if sk:
            shutil.rmtree(sk.dir_path)
            con.print(f"  [red]-[/red] Removed {sk.dir_path}")
            removed += 1

    if removed == 0:
        con.print(f"[red]Not found[/red]: {name}")
        raise typer.Exit(code=1)
    con.print(f"[green]Removed[/green] {removed} instance(s) of '{name}'.")


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


@app.command('mcp-serve')
def cmd_mcp_serve() -> None:
    """Start the MCP server (stdio transport) for skill browsing tools."""
    from .mcp_server import main as mcp_main
    mcp_main()


remote = typer.Typer(help='Remote helpers.')
app.add_typer(remote, name='remote')

@remote.command('stats')
def cmd_remote_stats() -> None:
    from .remote_tools import remote_stats
    remote_stats(OoaiSkillsSettings(), console=Console())

@remote.command('search')
def cmd_remote_search(
    pattern: Annotated[str, typer.Argument(help='Search pattern.')],
    limit: Annotated[int, typer.Option('--limit')] = 50,
) -> None:
    """Search the remote MinIO registry for skills."""
    from .sync import remote_search
    con = Console()
    hits = remote_search(pattern, OoaiSkillsSettings(), console=con)
    table = Table(title=f"Remote search '{pattern}' ({min(limit, len(hits))}/{len(hits)})")
    table.add_column("Name", style="bold")
    table.add_column("Source", style="cyan")
    table.add_column("Description")
    for sk in hits[:limit]:
        table.add_row(sk.name, sk.source_repo, sk.description[:100])
    con.print(table)


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
