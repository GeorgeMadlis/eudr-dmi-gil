from __future__ import annotations

import mimetypes
import os
from pathlib import Path

from minio import Minio
from minio.error import S3Error


def _client_from_env() -> Minio:
    endpoint = os.environ.get("MINIO_ENDPOINT", "").strip()
    access_key = os.environ.get("MINIO_ACCESS_KEY", "").strip()
    secret_key = os.environ.get("MINIO_SECRET_KEY", "").strip()
    secure_env = os.environ.get("MINIO_SECURE", "true").strip().lower()
    secure = secure_env not in {"0", "false", "no"}

    if not endpoint or not access_key or not secret_key:
        raise RuntimeError("Missing MINIO_ENDPOINT/MINIO_ACCESS_KEY/MINIO_SECRET_KEY")

    return Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)


def ensure_bucket(endpoint: str, access_key: str, secret_key: str, bucket: str) -> None:
    client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=True)
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def put_file(bucket: str, key: str, local_path: Path, content_type: str | None = None) -> None:
    client = _client_from_env()
    if content_type is None:
        content_type, _ = mimetypes.guess_type(str(local_path))
    client.fput_object(bucket, key, str(local_path), content_type=content_type)


def get_file_if_exists(bucket: str, key: str, dest_path: Path) -> bool:
    client = _client_from_env()
    try:
        client.stat_object(bucket, key)
    except S3Error as exc:
        if exc.code in {"NoSuchKey", "NoSuchObject", "NoSuchBucket"}:
            return False
        raise

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    client.fget_object(bucket, key, str(dest_path))
    return True