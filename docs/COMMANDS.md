# Commands reference

## Setup
- `ooai-skills init [DIR]` — scaffold multi-agent directory structure (Claude Code, Deep Agents, Codex, Gemini)

## Registry + pull
- `ooai-skills pull --all [--copy] [--target DIR ...] [--no-extra]` — pull index → cache → flattened view(s)

## Ingestion
- `ooai-skills push-local <dir> --pack <name>` — upload local skill folders into MinIO
- `ooai-skills mirror <sources.yaml>` — mirror repos via git clone (with ZIP fallback)
- `ooai-skills mirror-curated --category ... --kinds ...` — mirror curated repos via git
- `ooai-skills ingest-github-zip <owner/repo> [--ref main] [--github-token ...]` — ingest via GitHub archive ZIP (no git)
- `ooai-skills ingest-curated-zips --category ... --kinds ...` — ingest curated repos via ZIP (batch)

## Curated list
- `ooai-skills curated categories`
- `ooai-skills curated list [--category ...] [--kind ...]`
- `ooai-skills curated export <out.yaml> ...`

## Local browsing
- `ooai-skills local list [--root DIR] [--limit N]`
- `ooai-skills local find <text> [--root DIR] [--limit N]`
- `ooai-skills local info <name> [--root DIR]`
- `ooai-skills local cat <name> [--root DIR] [--head N]`

## Remote
- `ooai-skills remote stats` — show MinIO bucket name and skill count

## MCP server
- `ooai-skills mcp-serve` — start MCP server (stdio transport) exposing skill browsing tools
