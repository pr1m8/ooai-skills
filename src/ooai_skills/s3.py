"""MinIO/S3 adapter."""

from __future__ import annotations

import io
import json
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable

from minio import Minio
from minio.error import S3Error

from .settings import OoaiSkillsSettings

# Callback type: (bucket, key, size_bytes) -> None
UploadNotifyCallback = Callable[[str, str, int], None]


@dataclass
class S3Client:
    client: Minio
    bucket: str
    on_upload: list[UploadNotifyCallback] = field(default_factory=list)

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

    def _notify(self, key: str, size: int) -> None:
        for cb in self.on_upload:
            cb(self.bucket, key, size)

    def put_json(self, key: str, data: dict[str, Any]) -> None:
        payload = json.dumps(data, indent=2, sort_keys=True).encode("utf-8")
        bio = io.BytesIO(payload)
        clean_key = key.lstrip("/")
        self.client.put_object(self.bucket, clean_key, bio, len(payload), content_type="application/json")
        self._notify(clean_key, len(payload))

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
            key = f"{prefix.rstrip('/')}/{rel}".lstrip("/")
            size = p.stat().st_size
            with p.open("rb") as f:
                self.client.put_object(self.bucket, key, f, size)
            self._notify(key, size)

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

    # --- Presigned URLs ---

    def presigned_get(self, key: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate a presigned GET URL for downloading an object."""
        return self.client.presigned_get_object(self.bucket, key.lstrip("/"), expires=expires)

    def presigned_put(self, key: str, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate a presigned PUT URL for uploading an object."""
        return self.client.presigned_put_object(self.bucket, key.lstrip("/"), expires=expires)
