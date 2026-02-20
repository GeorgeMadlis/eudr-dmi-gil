from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    if not slug:
        raise ValueError("empty slug")
    return slug


def read_json_file(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_optional_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    return read_json_file(path)


def write_json_stable(path: str | Path, payload: dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_text(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def sha256_file(path: str | Path, *, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest_sha256(out_dir: str | Path, filenames: list[str]) -> Path:
    out_path = Path(out_dir)
    lines: list[str] = []
    for name in filenames:
        file_path = out_path / name
        lines.append(f"{sha256_file(file_path)}  {name}")

    manifest_path = out_path / "manifest.sha256"
    write_text(manifest_path, "\n".join(lines) + "\n")
    return manifest_path
