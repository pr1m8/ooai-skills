"""Frontmatter parsing for SKILL.md."""

from __future__ import annotations

from typing import Any, TypedDict

import yaml


class ParsedFrontmatter(TypedDict):
    frontmatter: dict[str, Any]
    body: str


def parse_frontmatter(markdown: str) -> ParsedFrontmatter:
    text = markdown.lstrip("\ufeff")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {"frontmatter": {}, "body": markdown}
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {"frontmatter": {}, "body": markdown}
    yaml_text = "\n".join(lines[1:end_idx]).strip()
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    if not yaml_text:
        return {"frontmatter": {}, "body": body}
    parsed = yaml.safe_load(yaml_text) or {}
    if not isinstance(parsed, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return {"frontmatter": parsed, "body": body}
