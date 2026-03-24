"""Settings for :mod:`ooai_skills` (Pydantic v2).

Reads from environment variables with prefix ``OOAI_SKILLS_``.  When running
inside the ooai docker stack the existing ``MINIO_*`` variables are accepted
as aliases, so no extra configuration is required.

Resolution priority (first match wins):

- ``OOAI_SKILLS_S3_ENDPOINT``       → explicit override
- ``MINIO_PORT``                     → builds ``http://localhost:{port}``
- default                            → ``http://localhost:9000``

Examples:
    ::
        >>> from ooai_skills.settings import OoaiSkillsSettings
        >>> s = OoaiSkillsSettings()
        >>> s.local_skills_dir.as_posix().endswith("/.agents/skills")
        True
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _expand_path(value: str) -> Path:
    if not value:
        raise ValueError("Path must not be empty.")
    return Path(value).expanduser()


def _default_endpoint() -> str:
    """Build MinIO endpoint from MINIO_PORT when present."""
    port = os.environ.get("MINIO_PORT", "9000")
    return f"http://localhost:{port}"


class OoaiSkillsSettings(BaseSettings):
    """Configuration for MinIO + local cache.

    Works out of the box with the ooai docker stack: reads the existing
    ``MINIO_ROOT_USER`` / ``MINIO_ROOT_PASSWORD`` / ``MINIO_PORT`` env
    vars that are already exported from the ooai ``.env`` file.
    Additional ``OOAI_SKILLS_*`` or legacy ``SKILL_MIRROR_*`` variables
    always take precedence.
    """

    model_config = SettingsConfigDict(
        env_prefix="OOAI_SKILLS_",
        env_file=(".env", "packages/ooai-skills/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    s3_endpoint: Annotated[
        str,
        Field(
            min_length=1,
            validation_alias=AliasChoices(
                "OOAI_SKILLS_S3_ENDPOINT",
                "SKILL_MIRROR_S3_ENDPOINT",
            ),
        ),
    ] = Field(default_factory=_default_endpoint)

    s3_access_key: Annotated[
        str,
        Field(
            min_length=1,
            validation_alias=AliasChoices(
                "OOAI_SKILLS_S3_ACCESS_KEY",
                "SKILL_MIRROR_S3_ACCESS_KEY",
                "MINIO_ROOT_USER",
            ),
        ),
    ] = "minioadmin"

    s3_secret_key: Annotated[
        str,
        Field(
            min_length=1,
            validation_alias=AliasChoices(
                "OOAI_SKILLS_S3_SECRET_KEY",
                "SKILL_MIRROR_S3_SECRET_KEY",
                "MINIO_ROOT_PASSWORD",
            ),
        ),
    ] = "minioadmin"

    s3_secure: bool = Field(
        default=False,
        validation_alias=AliasChoices(
            "OOAI_SKILLS_S3_SECURE",
            "SKILL_MIRROR_S3_SECURE",
        ),
    )

    s3_region: str = Field(
        default="us-east-1",
        validation_alias=AliasChoices(
            "OOAI_SKILLS_S3_REGION",
            "SKILL_MIRROR_S3_REGION",
        ),
    )

    bucket: Annotated[
        str,
        Field(
            min_length=1,
            validation_alias=AliasChoices(
                "OOAI_SKILLS_BUCKET",
                "SKILL_MIRROR_BUCKET",
            ),
        ),
    ] = "agent-skills"

    local_packs_dir: Path = Field(
        default_factory=lambda: _expand_path("~/.agents/skillpacks"),
    )
    local_skills_dir: Path = Field(
        default_factory=lambda: _expand_path("~/.agents/skills"),
    )
    work_dir: Path = Field(
        default_factory=lambda: _expand_path("~/.cache/ooai-skills"),
    )

    @field_validator("s3_endpoint", mode="before")
    @classmethod
    def _normalise_endpoint(cls, v: object) -> object:
        """Accept bare host:port (without scheme) and add http://."""
        if isinstance(v, str) and v and not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v
