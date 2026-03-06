"""Settings for :mod:`ooai_skills` (Pydantic v2).

Examples:
    ::
        >>> from ooai_skills.settings import OoaiSkillsSettings
        >>> s = OoaiSkillsSettings()
        >>> s.local_skills_dir.as_posix().endswith("/.agents/skills")
        True
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _expand_path(value: str) -> Path:
    if not value:
        raise ValueError("Path must not be empty.")
    return Path(value).expanduser()


class OoaiSkillsSettings(BaseSettings):
    """Configuration for MinIO + local cache."""

    model_config = SettingsConfigDict(env_prefix="OOAI_SKILLS_", env_file=".env", extra="ignore")

    s3_endpoint: Annotated[str, Field(min_length=1, validation_alias=AliasChoices("OOAI_SKILLS_S3_ENDPOINT", "SKILL_MIRROR_S3_ENDPOINT"))] = "http://localhost:9000"
    s3_access_key: Annotated[str, Field(min_length=1, validation_alias=AliasChoices("OOAI_SKILLS_S3_ACCESS_KEY", "SKILL_MIRROR_S3_ACCESS_KEY"))] = "minioadmin"
    s3_secret_key: Annotated[str, Field(min_length=1, validation_alias=AliasChoices("OOAI_SKILLS_S3_SECRET_KEY", "SKILL_MIRROR_S3_SECRET_KEY"))] = "minioadmin"
    s3_secure: bool = Field(default=False, validation_alias=AliasChoices("OOAI_SKILLS_S3_SECURE", "SKILL_MIRROR_S3_SECURE"))
    s3_region: str = Field(default="us-east-1", validation_alias=AliasChoices("OOAI_SKILLS_S3_REGION", "SKILL_MIRROR_S3_REGION"))
    bucket: Annotated[str, Field(min_length=1, validation_alias=AliasChoices("OOAI_SKILLS_BUCKET", "SKILL_MIRROR_BUCKET"))] = "agent-skills"

    local_packs_dir: Path = Field(default_factory=lambda: _expand_path("~/.agents/skillpacks"))
    local_skills_dir: Path = Field(default_factory=lambda: _expand_path("~/.agents/skills"))
    work_dir: Path = Field(default_factory=lambda: _expand_path("~/.cache/ooai-skills"))
