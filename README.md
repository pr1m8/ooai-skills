# ooai-skills

`ooai-skills` stores SKILL.md skill packs in MinIO and pulls them into:
- `~/.agents/skillpacks/` (cache)
- `~/.agents/skills/` (flattened view)

## Setup
```bash
cp .env.example .env
pdm add -dG dev -e .
```

## Push local skills into MinIO (no Git needed)
```bash
pdm run ooai-skills push-local /path/to/skills --pack my-pack
```

## Pull from MinIO into local
```bash
pdm run ooai-skills pull --all
```

## Browse local
```bash
pdm run ooai-skills local list
pdm run ooai-skills local find pandas
pdm run ooai-skills local info pandas
pdm run ooai-skills local cat pandas --head 80
```

## Curated list
```bash
pdm run ooai-skills curated categories
pdm run ooai-skills curated list --category "Core general skill catalogs"
```

## Mirror from GitHub
```bash
pdm run ooai-skills curated export sources.yaml --kinds skills --all-categories
pdm run ooai-skills mirror sources.yaml
```
Or mirror curated categories directly:
```bash
pdm run ooai-skills mirror-curated --category "Core general skill catalogs" --category "Security-focused packs"
```

## Remote stats (full variant)
```bash
pdm run ooai-skills remote stats
```


## Documentation
See `docs/INDEX.md`.
