# Model Context Protocol (MCP)

Open standard for connecting AI agents to external systems. Maintained by Anthropic, adopted broadly across the ecosystem.

## What It Is

MCP is a universal connector ("USB-C for AI") that lets any AI host talk to any external service through a standard protocol. Instead of each agent building custom integrations, MCP provides one protocol that works everywhere.

## Architecture

```
┌─────────────────────────────────────────┐
│  MCP Host (Claude Code, Cursor, etc.)   │
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌────────┐  │
│  │ Client 1 │  │ Client 2 │  │Client N│  │
│  └────┬─────┘  └────┬─────┘  └───┬────┘  │
└───────┼──────────────┼────────────┼───────┘
        │              │            │
   ┌────▼────┐   ┌─────▼───┐  ┌────▼────┐
   │ Server  │   │ Server  │  │ Server  │
   │ (files) │   │ (DB)    │  │ (API)   │
   └─────────┘   └─────────┘  └─────────┘
```

- **Host:** The AI application (Claude Code, Cursor, VS Code Copilot)
- **Client:** One per server, lives inside the host, translates between LLM and MCP protocol
- **Server:** External service exposing tools, resources, or prompts
- **Transport:** JSON-RPC 2.0 over `stdio` (local processes) or `SSE` (remote HTTP)

## Three Primitives

| Primitive | What it does | Side effects? | Example |
|-----------|-------------|---------------|---------|
| **Tools** | Actions the model can invoke | Yes | Run a query, create a file, call an API |
| **Resources** | Data the model can read | No | Database schema, file contents, config |
| **Prompts** | Reusable message templates | No | "Summarize this PR", "Debug this error" |

**Key distinction:** Tools *do* things. Resources *provide* knowledge. Prompts *guide* interactions.

## Configuration

### `.mcp.json` (project root)

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"],
      "env": {}
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "postgresql://..." }
    }
  }
}
```

### Also configurable in

- `.claude/settings.json` → `mcpServers` key
- `.claude/settings.local.json` → personal MCP servers (gitignored)
- `~/.claude/settings.json` → user-global MCP servers

### Our project's MCP setup

`.claude/settings.local.json` enables `docs-langchain` (Context7-based documentation server) and all project MCP servers.

## Tool Search

Claude Code uses dynamic tool loading to manage context budget:

- Not all MCP tool definitions loaded at once
- ~8,700 tokens regardless of how many servers are configured
- Tools fetched on-demand based on task context
- Automatic on Sonnet 4+ and Opus 4+

This means adding more MCP servers does not linearly increase context usage.

## MCP vs Skills

| Aspect | MCP Tools | Skills |
|--------|-----------|--------|
| **What** | Runtime access to external systems | Instruction templates for tasks |
| **Format** | Code-based servers (TypeScript/Python) | Markdown files (SKILL.md) |
| **Token cost** | ~8,700 total (with Tool Search) | ~100 per skill description |
| **Side effects** | Yes (tools can modify state) | No (instructions only; agent decides what to do) |
| **Who decides** | LLM chooses when to call tools | LLM or user activates skill |
| **Portability** | Cross-agent (MCP standard) | Cross-agent (SKILL.md standard) |

**They complement each other:**
- A skill describes *how* to approach a task (procedure, best practices)
- MCP tools provide *access* to the systems needed (APIs, databases, files)
- Example: a "deploy" skill references MCP tools for AWS/Docker interaction

## How ooai-skills Relates

- Our project uses MCP for docs access (Context7 / docs-langchain server)
- Skills we curate are instructions only — they may reference tools but don't provide them
- **Future opportunity:** Build an MCP server wrapping our `local list/find/cat` commands
  - Agent could ask "find me a skill for kubernetes deployment" at runtime
  - Maps directly to our existing CLI: `ooai-skills local find kubernetes`
  - Would let any MCP-compatible agent search our curated skill registry
