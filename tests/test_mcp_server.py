from __future__ import annotations

import json
from pathlib import Path

from ooai_skills.mcp_server import _handle_request, _handle_list_skills, _handle_find_skills


def _make_skill_dir(root: Path, name: str, desc: str = "test") -> None:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\n", encoding="utf-8")


def test_initialize() -> None:
    resp = _handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["id"] == 1
    assert "ooai-skills" in resp["result"]["serverInfo"]["name"]


def test_tools_list() -> None:
    resp = _handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = resp["result"]["tools"]
    names = {t["name"] for t in tools}
    assert "list_skills" in names
    assert "find_skills" in names
    assert "get_skill_info" in names
    assert "read_skill" in names


def test_list_skills(tmp_path: Path) -> None:
    _make_skill_dir(tmp_path, "alpha", "first skill")
    _make_skill_dir(tmp_path, "beta", "second skill")
    result = json.loads(_handle_list_skills({"root": str(tmp_path)}))
    assert len(result) == 2
    names = {s["name"] for s in result}
    assert "alpha" in names
    assert "beta" in names


def test_find_skills(tmp_path: Path) -> None:
    _make_skill_dir(tmp_path, "deploy-app", "Deploy application")
    _make_skill_dir(tmp_path, "test-runner", "Run tests")
    result = json.loads(_handle_find_skills({"root": str(tmp_path), "pattern": "deploy"}))
    assert len(result) == 1
    assert result[0]["name"] == "deploy-app"


def test_list_skills_missing_dir(tmp_path: Path) -> None:
    """Should return empty list, not crash."""
    result = json.loads(_handle_list_skills({"root": str(tmp_path / "nonexistent")}))
    assert result == []


def test_tools_call(tmp_path: Path) -> None:
    _make_skill_dir(tmp_path, "my-skill", "does things")
    resp = _handle_request({
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "list_skills", "arguments": {"root": str(tmp_path)}},
    })
    text = resp["result"]["content"][0]["text"]
    skills = json.loads(text)
    assert len(skills) == 1
    assert skills[0]["name"] == "my-skill"


def test_unknown_tool() -> None:
    resp = _handle_request({
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "nonexistent", "arguments": {}},
    })
    assert resp["result"]["isError"] is True


def test_unknown_method() -> None:
    resp = _handle_request({"jsonrpc": "2.0", "id": 5, "method": "foo/bar"})
    assert "error" in resp
    assert resp["error"]["code"] == -32601


def test_ping() -> None:
    resp = _handle_request({"jsonrpc": "2.0", "id": 6, "method": "ping"})
    assert resp["id"] == 6
    assert resp["result"] == {}
