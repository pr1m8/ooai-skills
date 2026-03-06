# Curated repo list

ooai-skills embeds a categorized allowlist of repositories (skill packs + tooling + directories).

## Browse categories
```bash
ooai-skills curated categories
```

## List repos in a category
```bash
ooai-skills curated list --category "Cloud / infra platform packs"
```

## Filter by kind
Kinds are informational tags such as: `skills`, `tooling`, `spec`, `examples`, `directory`.

```bash
ooai-skills curated list --kind skills
```

## Export to a sources.yaml
This is useful if you prefer the git-based mirror path.

```bash
ooai-skills curated export sources.yaml --kinds skills --all-categories
```

## Ingest curated categories by ZIP
```bash
ooai-skills ingest-curated-zips --category "Core general skill catalogs" --kinds skills --github-token "$OOAI_SKILLS_GITHUB_TOKEN"
```
