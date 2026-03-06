# Commands reference

## Registry + pull
- `ooai-skills verify` — MinIO read/write probe + local dir checks
- `ooai-skills pull --all [--copy] [--target DIR ...]` — pull index → cache → flattened view(s)

## Ingestion
- `ooai-skills push-local <dir> --pack <name>` — upload local skill folders into MinIO
- `ooai-skills ingest-github-zip <owner/repo> [--ref main] [--github-token ...]` — ingest via GitHub archive ZIP (no git)
- `ooai-skills ingest-curated-zips --category ... --kinds ...` — ingest curated repos via ZIP (batch)

## Curated list
- `ooai-skills curated categories`
- `ooai-skills curated list [--category ...] [--kind ...]`
- `ooai-skills curated export <out.yaml> ...`

## Local browsing
- `ooai-skills local list`
- `ooai-skills local find <text>`
- `ooai-skills local info <name>`
- `ooai-skills local cat <name> [--head N]`
