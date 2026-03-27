"""Generalized installer: download from GitHub and route to correct locations.

Handles all resource types:
- skills (SKILL.md) → .claude/skills/, .agents/skills/, ~/.agents/skills/, ~/.claude/skills/
- commands (.md) → .claude/commands/
- agents (.md) → .claude/agents/, .agents/personas/
- rules (.md, .mdc, .cursorrules) → .claude/rules/, .agents/rules/, .cursor/rules/
- mcp configs (.json) → .mcp.json merge
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from .discover import discover_skills
from .git import clone_repo
from .models import RepoSource
from .settings import OoaiSkillsSettings


@dataclass
class InstallResult:
    """Summary of what was installed."""
    skills: int = 0
    commands: int = 0
    agents: int = 0
    rules: int = 0
    files: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.skills + self.commands + self.agents + self.rules


def _discover_commands(repo_dir: Path) -> list[Path]:
    """Find .claude/commands/*.md or commands/*.md files."""
    found: list[Path] = []
    for pattern in ["**/commands/*.md", "**/.claude/commands/*.md"]:
        found.extend(repo_dir.glob(pattern))
    return sorted(set(found))


def _discover_agents(repo_dir: Path) -> list[Path]:
    """Find agent definition files."""
    found: list[Path] = []
    for pattern in ["**/agents/*.md", "**/.claude/agents/*.md", "**/personas/*.md"]:
        found.extend(repo_dir.glob(pattern))
    return sorted(set(found))


def _discover_rules(repo_dir: Path) -> list[Path]:
    """Find rule files (.md, .mdc, .cursorrules)."""
    found: list[Path] = []
    for pattern in [
        "**/rules/*.md", "**/rules/*.mdc",
        "**/.cursorrules", "**/.cursor/rules/*.mdc",
        "**/.claude/rules/*.md", "**/.agents/rules/*.md",
    ]:
        found.extend(repo_dir.glob(pattern))
    return sorted(set(found))


def install_from_github(
    repo: str,
    *,
    ref: str = "main",
    what: str = "all",
    name_filter: str | None = None,
    settings: OoaiSkillsSettings,
    console: Console | None = None,
) -> InstallResult:
    """Download from GitHub and install to local directories.

    Args:
        repo: GitHub repo in 'owner/name' format.
        ref: Branch or tag.
        what: What to install — 'all', 'skills', 'commands', 'agents', 'rules'.
        name_filter: If set, only install items matching this name.
        settings: Settings instance.
        console: Rich console.

    Returns:
        InstallResult with counts of what was installed.
    """
    con = console or Console()
    result = InstallResult()
    work = settings.work_dir.expanduser() / "direct"
    work.mkdir(parents=True, exist_ok=True)

    owner, rname = repo.split("/", 1)
    repo_dir = work / owner / rname

    con.print(f"Fetching [cyan]{repo}@{ref}[/cyan]...")
    sha = clone_repo(repo, ref, repo_dir)
    con.print(f"[dim]Resolved to {sha[:12]}[/dim]")

    skill_targets = [settings.local_skills_dir.expanduser()] + settings.resolved_extra_targets

    # --- Skills ---
    if what in ("all", "skills"):
        source = RepoSource(repo=repo, ref=ref)
        skills, _ = discover_skills(repo_dir, source, commit_sha=sha)
        if name_filter:
            skills = [s for s in skills if name_filter in s.name or name_filter in s.source_path]

        for sk in skills:
            src_dir = repo_dir / sk.source_path
            for target in skill_targets:
                target.mkdir(parents=True, exist_ok=True)
                dst = target / sk.name
                _replace_dir(src_dir, dst)
            result.skills += 1
            result.files.append(f"skill: {sk.name}")

    # --- Commands ---
    if what in ("all", "commands"):
        commands = _discover_commands(repo_dir)
        if name_filter:
            commands = [c for c in commands if name_filter in c.stem]

        cmd_dir = Path(".claude/commands")
        cmd_dir.mkdir(parents=True, exist_ok=True)
        for cmd_path in commands:
            dst = cmd_dir / cmd_path.name
            if not dst.exists():
                shutil.copy2(cmd_path, dst)
                result.commands += 1
                result.files.append(f"command: {cmd_path.name}")

    # --- Agents ---
    if what in ("all", "agents"):
        agents = _discover_agents(repo_dir)
        if name_filter:
            agents = [a for a in agents if name_filter in a.stem]

        for agent_path in agents:
            # Install to .claude/agents/
            claude_dst = Path(".claude/agents") / agent_path.name
            claude_dst.parent.mkdir(parents=True, exist_ok=True)
            if not claude_dst.exists():
                shutil.copy2(agent_path, claude_dst)

            # Also install to .agents/personas/
            agents_dst = Path(".agents/personas") / agent_path.name
            agents_dst.parent.mkdir(parents=True, exist_ok=True)
            if not agents_dst.exists():
                shutil.copy2(agent_path, agents_dst)

            result.agents += 1
            result.files.append(f"agent: {agent_path.name}")

    # --- Rules ---
    if what in ("all", "rules"):
        rules = _discover_rules(repo_dir)
        if name_filter:
            rules = [r for r in rules if name_filter in r.stem]

        for rule_path in rules:
            # Route by extension
            if rule_path.suffix == ".mdc" or ".cursor" in str(rule_path):
                dst = Path(".cursor/rules") / rule_path.name
            elif ".claude" in str(rule_path):
                dst = Path(".claude/rules") / rule_path.name
            else:
                dst = Path(".agents/rules") / rule_path.name

            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                shutil.copy2(rule_path, dst)
                result.rules += 1
                result.files.append(f"rule: {rule_path.name}")

    # Report
    if result.total == 0:
        con.print(f"[yellow]No {what} found[/yellow] in {repo}")
    else:
        con.print(f"[green]Installed[/green] {result.total} item(s) from {repo}:")
        for f in result.files:
            con.print(f"  [green]+[/green] {f}")

    return result


def install_from_url(
    url: str,
    *,
    what: str = "all",
    settings: OoaiSkillsSettings,
    console: Console | None = None,
) -> InstallResult:
    """Install from a GitHub URL.

    Supports:
    - https://github.com/owner/repo
    - https://github.com/owner/repo/tree/branch/path
    - owner/repo
    """
    con = console or Console()
    url = url.strip().rstrip("/")
    if url.startswith("https://github.com/"):
        url = url.removeprefix("https://github.com/")

    parts = url.split("/")
    if len(parts) < 2:
        con.print(f"[red]Invalid repo:[/red] {url}")
        return InstallResult()

    repo = f"{parts[0]}/{parts[1]}"
    ref = "main"
    name_filter = None

    if len(parts) >= 4 and parts[2] == "tree":
        ref = parts[3]
        if len(parts) >= 5:
            name_filter = parts[-1]

    return install_from_github(
        repo, ref=ref, what=what, name_filter=name_filter,
        settings=settings, console=con,
    )


def _replace_dir(src: Path, dst: Path) -> None:
    """Copy src to dst, replacing dst if it exists."""
    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.copytree(src, dst)
