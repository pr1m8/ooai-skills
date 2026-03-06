"""Models for :mod:`ooai_skills`."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class RepoSource(BaseModel):
    repo: str = Field(min_length=3)
    ref: str = "main"
    include_globs: list[str] = Field(default_factory=list)
    exclude_globs: list[str] = Field(default_factory=list)

    @field_validator("repo")
    @classmethod
    def _v_repo(cls, v: str) -> str:
        if v.count("/") != 1 or any(not p for p in v.split("/", 1)):
            raise ValueError("repo must be in 'owner/name' form")
        return v


class SkillRecord(BaseModel):
    skill_id: str
    name: str = Field(min_length=1)
    description: str = ""
    source_repo: str
    source_commit: str
    source_path: str
    content_hash: str
    s3_prefix: str
    frontmatter: dict[str, Any] = Field(default_factory=dict)
    discovered_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")


class SkillIndex(BaseModel):
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    skills: list[SkillRecord] = Field(default_factory=list)


class SourceIndex(BaseModel):
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    sources: dict[str, str] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)


class LintIssue(BaseModel):
    skill_id: str
    severity: Literal["error", "warning"]
    code: str
    message: str
    path: str | None = None


class LintIndex(BaseModel):
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(timespec="seconds") + "Z")
    issues: list[LintIssue] = Field(default_factory=list)


class CuratedRepo(BaseModel):
    repo: str
    category: str
    kind: str
    description: str = ""
