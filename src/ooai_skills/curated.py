"""Embedded curated repository list."""

from __future__ import annotations

import json
from importlib import resources

from .models import CuratedRepo


def all_repos() -> list[CuratedRepo]:
    raw = resources.files("ooai_skills.data").joinpath("curated.json").read_text(encoding="utf-8")
    items = json.loads(raw)
    return [CuratedRepo(**it) for it in items]


def categories() -> list[str]:
    return sorted({r.category for r in all_repos()})


def filter_repos(*, category: str | None = None, kinds: set[str] | None = None) -> list[CuratedRepo]:
    repos = all_repos()
    if category is not None:
        repos = [r for r in repos if r.category == category]
    if kinds is not None:
        repos = [r for r in repos if r.kind in kinds]
    return repos
