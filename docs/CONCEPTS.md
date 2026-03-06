# Concepts and layout

## What is a “skill”?
A **skill** is any directory containing a file named `SKILL.md`.

## What does ooai-skills do?
ooai-skills provides a practical “registry + cache” workflow:

1) **Registry (MinIO/S3)** stores skill directories under stable prefixes and maintains an index.
2) **Pull** downloads those skills to your machine and builds a flattened view directory for discovery.

## Remote layout (MinIO)
- Skill objects are stored under `packs/...`
- Indexes are stored under `index/...`

Indexes:
- `index/skills.json` — the source of truth for what to pull
- `index/sources.json` — which sources were ingested (best effort)
- `index/lint.json` — warnings/errors found during discovery

## Local layout
- Cache: `~/.agents/skillpacks/<owner>/<repo>/<skill-path>/...`
- Flattened view: `~/.agents/skills/<skill-name>/...`

The flattened view is rebuilt from the cache every time you run `pull`.

## Why a flattened view?
Many agent tools expect a single directory of skill folders. Flattening also avoids
needing to remember per-repo nesting.
