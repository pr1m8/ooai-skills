# Research Notes

Knowledge base for the agent skills ecosystem — standards, infrastructure, and integration points.

`docs/` = how to use ooai-skills (operational).
`notes/` = how the ecosystem works and where we fit (knowledge base).

## Reading Order

| # | File | What it covers |
|---|------|---------------|
| 1 | [CLAUDE_CODE_INFRASTRUCTURE](CLAUDE_CODE_INFRASTRUCTURE.md) | **Start here.** Full `.claude/` folder structure E2E — project, user, enterprise scopes, permissions, loading order |
| 2 | [SKILL_MD_STANDARD](SKILL_MD_STANDARD.md) | The SKILL.md format (agentskills.io) — frontmatter schema, directory layout, progressive disclosure, validation |
| 3 | [CLAUDE_CODE_SKILLS](CLAUDE_CODE_SKILLS.md) | Claude Code extensions to SKILL.md — fork context, effort, auto-activation, dynamic substitutions |
| 4 | [MEMORY_AND_CONTEXT](MEMORY_AND_CONTEXT.md) | CLAUDE.md, auto-memory (MEMORY.md), rules/, imports, context loading across agents |
| 5 | [MCP](MCP.md) | Model Context Protocol — architecture, primitives (tools/resources/prompts), configuration |
| 6 | [DOTAGENTS_AND_CONVENTIONS](DOTAGENTS_AND_CONVENTIONS.md) | `.agents/` standard, Deep Agents framework, Vercel skills CLI, convention conflicts |
| 7 | [INTEGRATION_MAP](INTEGRATION_MAP.md) | How ooai-skills connects to each piece — current state, gaps, next steps |
