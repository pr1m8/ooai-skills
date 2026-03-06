"""Load sources.yaml/json for Git mirroring."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from .models import RepoSource


def load_sources_file(path: Path) -> list[RepoSource]:
    if not path.exists():
        raise FileNotFoundError(str(path))
    raw = path.read_text(encoding="utf-8")
    doc = json.loads(raw) if path.suffix.lower() == ".json" else yaml.safe_load(raw)
    if not isinstance(doc, dict) or "sources" not in doc or not isinstance(doc["sources"], list):
        raise ValueError("sources file must be a mapping with key 'sources' as a list.")
    return [RepoSource(**item) for item in doc["sources"]]
