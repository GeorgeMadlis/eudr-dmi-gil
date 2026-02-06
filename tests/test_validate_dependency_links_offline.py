from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import importlib.util

import pytest


def _load_script_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, *, status: int, url: str, headers: dict[str, str]) -> None:
        self.status = status
        self._url = url
        self.headers = headers
        self.fp = SimpleNamespace(raw=SimpleNamespace(_sock=SimpleNamespace(settimeout=lambda _t: None)))

    def geturl(self) -> str:
        return self._url

    def read(self, _size: int = -1) -> bytes:
        return b""


def test_validate_dependency_links_offline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script_repo = Path(__file__).resolve().parents[1]
    validate_dependency_links = _load_script_module(
        script_repo / "scripts" / "validate_dependency_links.py",
        "validate_dependency_links",
    )

    repo_root = tmp_path
    docs = repo_root / "docs" / "dependencies"
    docs.mkdir(parents=True, exist_ok=True)
    sources_path = docs / "sources.json"
    sources_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "server_audit_root": "/audit",
                "sources": [
                    {
                        "id": "a_dep",
                        "url": "https://example.org/a",
                        "expected_content_type": "text/html",
                        "server_audit_path": "/audit/a",
                    },
                    {
                        "id": "b_dep",
                        "url": "https://example.org/b",
                        "expected_content_type": "application/json",
                        "server_audit_path": "/audit/b",
                    },
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    def fake_urlopen(request, timeout=0):  # noqa: ANN001
        method = request.get_method()
        url = request.full_url
        if url.endswith("/a"):
            return FakeResponse(status=200, url=url, headers={"Content-Type": "text/html"})
        if method == "HEAD":
            raise validate_dependency_links.urllib.error.HTTPError(
                url,
                405,
                "Method Not Allowed",
                {"Content-Type": "application/json"},
                None,
            )
        return FakeResponse(status=206, url=url, headers={"Content-Type": "application/json"})

    monkeypatch.setattr(validate_dependency_links, "repo_root", lambda: repo_root)
    monkeypatch.setattr(validate_dependency_links.urllib.request, "urlopen", fake_urlopen)

    out_path = repo_root / "out" / "dependency_link_check.json"
    result = validate_dependency_links.main(
        [
            "--sources-json",
            "docs/dependencies/sources.json",
            "--out",
            "out/dependency_link_check.json",
            "--no-timestamps",
        ]
    )
    assert result == 0
    assert out_path.exists()

    data = json.loads(out_path.read_text(encoding="utf-8"))
    ids = [entry["dependency_id"] for entry in data["results"]]
    assert ids == ["a_dep", "b_dep"]
    assert all("checked_at_utc" not in entry for entry in data["results"])
