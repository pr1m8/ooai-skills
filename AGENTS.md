# AGENTS

This repo is a small "skills registry" utility meant to support agent runtimes
that load **Agent Skills** (directories containing `SKILL.md`).

It gives you two concrete capabilities:

1) **Registry (MinIO/S3):** store skill folders under stable prefixes plus an index.
2) **Local view:** pull from the registry into a Deep-Agents-friendly layout:
   - `~/.agents/skillpacks/` (cache)
   - `~/.agents/skills/` (flattened view)

The flattened view is a practical convention: many agent tools can be pointed at
(or auto-discover) `~/.agents/skills/`.

## Core commands

### Push local skills into MinIO
Use this when you already have skills on disk (from cloned repos, `npx skills add`, zips, etc.).

```bash
ooai-skills push-local /path/to/skills-root --pack my-pack
```

A "skill" is any directory containing `SKILL.md`. The tool scans `**/SKILL.md`
and uploads each skill directory under the pack prefix.

### Pull from registry into local view
```bash
ooai-skills pull --all
```
(or `pull --pack my-pack` for one pack). This updates `~/.agents/skillpacks/`
and then flattens into `~/.agents/skills/`.

### Local browse
```bash
ooai-skills local list
ooai-skills local find <query>
ooai-skills local info <skill-id>
ooai-skills local cat <skill-id> [--head N]
```

See `README.md` and `docs/INDEX.md` for setup and more commands.
