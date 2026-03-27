"""MCP server exposing local skill browsing as tools.

Run standalone:
    python -m ooai_skills.mcp_server

Or configure in .mcp.json:
    {
      "mcpServers": {
        "ooai-skills": {
          "command": "python",
          "args": ["-m", "ooai_skills.mcp_server"]
        }
      }
    }
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .frontmatter import parse_frontmatter
from .local import find_local_skills, iter_local_skills, resolve_local_skill
from .settings import OoaiSkillsSettings

TOOLS = [
    {
        "name": "list_skills",
        "description": "List all locally installed agent skills.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "root": {"type": "string", "description": "Override skills root directory."},
                "limit": {"type": "integer", "description": "Max results (default 200)."},
            },
        },
    },
    {
        "name": "find_skills",
        "description": "Search local skills by name, description, or folder.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Search pattern (substring match)."},
                "root": {"type": "string", "description": "Override skills root directory."},
                "limit": {"type": "integer", "description": "Max results (default 50)."},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "get_skill_info",
        "description": "Get metadata for a specific skill by name.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill name or folder name."},
                "root": {"type": "string", "description": "Override skills root directory."},
            },
            "required": ["name"],
        },
    },
    {
        "name": "read_skill",
        "description": "Read the SKILL.md content for a specific skill.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Skill name or folder name."},
                "root": {"type": "string", "description": "Override skills root directory."},
                "head": {"type": "integer", "description": "Max lines to return (default 120)."},
            },
            "required": ["name"],
        },
    },
]


def _get_roots(args: dict) -> list[Path]:
    """Return all skill root directories to search."""
    if args.get("root"):
        return [Path(args["root"]).expanduser()]
    settings = OoaiSkillsSettings()
    roots = [settings.local_skills_dir.expanduser()]
    for extra in settings.resolved_extra_targets:
        if extra not in roots:
            roots.append(extra)
    return roots


def _get_root(args: dict) -> Path:
    """Return the primary skill root directory."""
    return _get_roots(args)[0]


def _safe_iter(root: Path) -> list:
    """Iterate skills, returning empty list if root doesn't exist."""
    if not root.exists():
        return []
    return list(iter_local_skills(root))


def _handle_list_skills(args: dict) -> str:
    limit = args.get("limit", 200)
    seen: set[str] = set()
    results: list[dict] = []
    for root in _get_roots(args):
        for sk in _safe_iter(root):
            if sk.name not in seen:
                seen.add(sk.name)
                results.append({"folder": sk.folder_name, "name": sk.name, "description": sk.description})
            if len(results) >= limit:
                break
    return json.dumps(results)


def _handle_find_skills(args: dict) -> str:
    limit = args.get("limit", 50)
    seen: set[str] = set()
    results: list[dict] = []
    for root in _get_roots(args):
        if not root.exists():
            continue
        for sk in find_local_skills(root, args["pattern"]):
            if sk.name not in seen:
                seen.add(sk.name)
                results.append({"folder": sk.folder_name, "name": sk.name, "description": sk.description})
            if len(results) >= limit:
                break
    return json.dumps(results)


def _handle_get_skill_info(args: dict) -> str:
    root = _get_root(args)
    if not root.exists():
        return json.dumps({"error": f"Skills directory not found: {root}"})
    sk = resolve_local_skill(root, args["name"])
    if not sk:
        return json.dumps({"error": f"Skill not found: {args['name']}"})
    skill_md = sk.dir_path / "SKILL.md"
    fm = {}
    if skill_md.exists():
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))["frontmatter"]
    return json.dumps({
        "folder": sk.folder_name,
        "name": sk.name,
        "description": sk.description,
        "path": str(sk.dir_path),
        "frontmatter": fm,
    })


def _handle_read_skill(args: dict) -> str:
    root = _get_root(args)
    if not root.exists():
        return json.dumps({"error": f"Skills directory not found: {root}"})
    sk = resolve_local_skill(root, args["name"])
    if not sk:
        return json.dumps({"error": f"Skill not found: {args['name']}"})
    skill_md = sk.dir_path / "SKILL.md"
    if not skill_md.exists():
        return json.dumps({"error": f"SKILL.md not found in {sk.dir_path}"})
    lines = skill_md.read_text(encoding="utf-8", errors="replace").splitlines()
    head = args.get("head", 120)
    if head > 0:
        lines = lines[:head]
    return "\n".join(lines)


_HANDLERS = {
    "list_skills": _handle_list_skills,
    "find_skills": _handle_find_skills,
    "get_skill_info": _handle_get_skill_info,
    "read_skill": _handle_read_skill,
}


def _write(msg: dict) -> None:
    raw = json.dumps(msg)
    sys.stdout.write(raw + "\n")
    sys.stdout.flush()


def _handle_request(req: dict) -> dict:
    method = req.get("method", "")
    rid = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": rid,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "ooai-skills", "version": "0.1.0"},
            },
        }

    if method == "notifications/initialized":
        return None  # type: ignore[return-value]

    if method == "ping":
        return {"jsonrpc": "2.0", "id": rid, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        handler = _HANDLERS.get(tool_name)
        if not handler:
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}], "isError": True},
            }
        try:
            result_text = handler(arguments)
        except Exception as e:
            return {
                "jsonrpc": "2.0", "id": rid,
                "result": {"content": [{"type": "text", "text": f"Error: {e}"}], "isError": True},
            }
        return {
            "jsonrpc": "2.0", "id": rid,
            "result": {"content": [{"type": "text", "text": result_text}]},
        }

    return {
        "jsonrpc": "2.0", "id": rid,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> None:
    """Run the MCP server over stdio (JSON-RPC 2.0, one message per line)."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        resp = _handle_request(req)
        if resp is not None:
            _write(resp)


if __name__ == "__main__":
    main()
