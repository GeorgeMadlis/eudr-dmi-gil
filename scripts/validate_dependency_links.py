#!/usr/bin/env python3
"""Validate dependency source links without downloading large bodies."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 20
RETRIES = 1


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_repo_relative(path: Path, *, label: str) -> None:
    if path.is_absolute():
        raise ValueError(f"{label} must be repo-relative (no absolute paths): {path}")


def resolve_under_repo(rel: Path) -> Path:
    root = repo_root().resolve()
    resolved = (root / rel).resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError(f"Path escapes repo root: {rel} -> {resolved}")
    return resolved


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _request_with_retries(request: urllib.request.Request) -> urllib.response.addinfourl:
    last_exc: Exception | None = None
    for attempt in range(RETRIES + 1):
        try:
            response = urllib.request.urlopen(request, timeout=CONNECT_TIMEOUT)  # noqa: S310
            return response
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < RETRIES:
                time.sleep(0.2)
                continue
            raise
    raise RuntimeError("unreachable") from last_exc


def _read_limited(response: urllib.response.addinfourl) -> None:
    try:
        sock = response.fp.raw._sock  # type: ignore[attr-defined]
        sock.settimeout(READ_TIMEOUT)
    except Exception:
        pass
    response.read(1024)


def _try_head(url: str) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, method="HEAD")
    response = _request_with_retries(req)
    status = getattr(response, "status", 200)
    final_url = response.geturl()
    headers = {k.lower(): v for k, v in response.headers.items()}
    return status, final_url, headers


def _try_get_range(url: str) -> tuple[int, str, dict[str, str]]:
    req = urllib.request.Request(url, method="GET")
    req.add_header("Range", "bytes=0-1024")
    response = _request_with_retries(req)
    status = getattr(response, "status", 200)
    final_url = response.geturl()
    headers = {k.lower(): v for k, v in response.headers.items()}
    _read_limited(response)
    return status, final_url, headers


def _check_url(url: str) -> tuple[int | None, str, dict[str, str]]:
    try:
        status, final_url, headers = _try_head(url)
        if status in {405, 501}:
            return _try_get_range(url)
        return status, final_url, headers
    except urllib.error.HTTPError as exc:
        if exc.code in {405, 501}:
            return _try_get_range(url)
        return exc.code, exc.geturl(), {k.lower(): v for k, v in exc.headers.items()}
    except Exception:
        return None, url, {}


def _normalize_sources(data: dict[str, Any], *, only: str | None) -> list[dict[str, Any]]:
    sources = data.get("sources") or []
    normalized: list[dict[str, Any]] = []
    for item in sources:
        if not isinstance(item, dict):
            continue
        dep_id = item.get("id")
        url = item.get("url")
        if not isinstance(dep_id, str) or not isinstance(url, str):
            continue
        if only and only not in dep_id:
            continue
        normalized.append(
            {
                "id": dep_id,
                "url": url,
                "expected_content_type": item.get("expected_content_type") or "",
                "server_audit_path": item.get("server_audit_path") or "",
            }
        )
    return sorted(normalized, key=lambda d: d["id"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate dependency source links")
    parser.add_argument(
        "--sources-json",
        default="docs/dependencies/sources.json",
        help="Repo-relative sources.json (default: docs/dependencies/sources.json)",
    )
    parser.add_argument(
        "--out",
        default="out/dependency_link_check.json",
        help="Repo-relative output JSON (default: out/dependency_link_check.json)",
    )
    parser.add_argument("--no-timestamps", action="store_true", help="Omit checked_at_utc")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit nonzero if any dependency link check fails",
    )
    parser.add_argument(
        "--only",
        default=None,
        help="Only check dependency_id entries containing this substring",
    )
    args = parser.parse_args(argv)

    try:
        sources_rel = Path(args.sources_json)
        out_rel = Path(args.out)
        ensure_repo_relative(sources_rel, label="--sources-json")
        ensure_repo_relative(out_rel, label="--out")
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    sources_path = resolve_under_repo(sources_rel)
    if not sources_path.exists():
        print(f"ERROR: sources JSON not found: {sources_path}", file=sys.stderr)
        return 2

    data = json.loads(sources_path.read_text(encoding="utf-8"))
    sources = _normalize_sources(data, only=args.only)

    results: list[dict[str, Any]] = []
    broken = 0
    for src in sources:
        status, final_url, headers = _check_url(src["url"])
        observed_content_type = headers.get("content-type", "")
        expected = src.get("expected_content_type", "")
        content_type_match = bool(expected and observed_content_type.startswith(expected))
        ok = status is not None and 200 <= status < 400
        if not ok:
            broken += 1
        entry = {
            "dependency_id": src["id"],
            "url": src["url"],
            "final_url": final_url,
            "http_status": status,
            "ok": ok,
            "observed_content_type": observed_content_type,
            "content_type_match": content_type_match,
            "expected_content_type": expected,
            "server_audit_path": src.get("server_audit_path", ""),
        }
        if not args.no_timestamps:
            entry["checked_at_utc"] = _now_utc_iso()
        results.append(entry)

    report = {
        "schema_version": "1.0",
        "sources_checked": len(results),
        "results": results,
    }

    out_path = resolve_under_repo(out_rel)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    for entry in results:
        status = entry.get("http_status")
        label = "OK" if entry.get("ok") else "FAIL"
        print(f"[{label}] {entry.get('dependency_id')} -> {status} {entry.get('final_url')}")

    if args.fail_on_broken and broken:
        print(f"ERROR: {broken} dependency link(s) failed", file=sys.stderr)
        return 3

    print(f"OK: wrote {out_rel.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
