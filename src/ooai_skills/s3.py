"""MinIO/S3 adapter."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from minio import Minio
from minio.error import S3Error

from .settings import OoaiSkillsSettings


@dataclass(frozen=True)
class S3Client:
    client: Minio
    bucket: str

    @staticmethod
    def from_settings(settings: OoaiSkillsSettings) -> "S3Client":
        endpoint = settings.s3_endpoint.replace("https://", "").replace("http://", "")
        mc = Minio(
            endpoint=endpoint,
            access_key=settings.s3_access_key,
            secret_key=settings.s3_secret_key,
            secure=settings.s3_secure,
            region=settings.s3_region,
        )
        c = S3Client(client=mc, bucket=settings.bucket)
        c.ensure_bucket()
        return c

    def ensure_bucket(self) -> None:
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise RuntimeError(f"Failed to ensure bucket {self.bucket}: {e}") from e

    def put_json(self, key: str, data: dict[str, Any]) -> None:
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        bio = io.BytesIO(payload)
        self.client.put_object(self.bucket, key.lstrip("/"), bio, len(payload), content_type="application/json")

    def get_json(self, key: str) -> dict[str, Any] | None:
        try:
            resp = self.client.get_object(self.bucket, key.lstrip("/"))
        except S3Error:
            return None
        try:
            return json.loads(resp.read().decode("utf-8"))
        finally:
            resp.close()
            resp.release_conn()

    def upload_dir(self, local_dir: Path, prefix: str) -> None:
        if not local_dir.exists():
            raise FileNotFoundError(str(local_dir))
        for p in sorted(local_dir.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(local_dir).as_posix()
            key = f"{prefix.rstrip('/')}/{rel}"
            with p.open("rb") as f:
                self.client.put_object(self.bucket, key.lstrip("/"), f, p.stat().st_size)

    def download_prefix(self, prefix: str, dest_dir: Path) -> int:
        dest_dir.mkdir(parents=True, exist_ok=True)
        count = 0
        prefix2 = prefix.lstrip("/")
        for obj in self.client.list_objects(self.bucket, prefix=prefix2, recursive=True):
            if obj.is_dir:
                continue
            rel = obj.object_name[len(prefix2):].lstrip("/")
            out_path = dest_dir / rel
            out_path.parent.mkdir(parents=True, exist_ok=True)
            resp = self.client.get_object(self.bucket, obj.object_name)
            try:
                out_path.write_bytes(resp.read())
                count += 1
            finally:
                resp.close()
                resp.release_conn()
        return count
