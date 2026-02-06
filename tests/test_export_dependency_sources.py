from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest


def _load_script_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_minimal_seed(path: Path, header: str, rows: list[str]) -> None:
    path.write_text("\n".join([header, *rows]) + "\n", encoding="utf-8")


def test_export_dependency_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    duckdb = pytest.importorskip("duckdb")
    _ = duckdb  # silence unused warning

    repo_root = tmp_path
    data_db = repo_root / "data_db"
    data_db.mkdir(parents=True, exist_ok=True)

    _write_minimal_seed(
        data_db / "dataset_catalogue_auto.csv",
        "dataset_id,name",
        ["ds-1,Example"],
    )
    _write_minimal_seed(
        data_db / "dataset_families_summary.csv",
        "dataset_id,family",
        ["ds-1,Example"],
    )
    _write_minimal_seed(
        data_db / "dependency_sources.csv",
        "dependency_id,url,expected_content_type,server_audit_path,description,family_or_tag,used_by",
        [
            "b_dep,https://example.org/b,text/html,/audit/b,B dep,tag-a,src/b.py",
            "a_dep,https://example.org/a,application/json,/audit/a,A dep,tag-b,src/a.py",
        ],
    )

    script_repo = Path(__file__).resolve().parents[1]
    bootstrap_data_db = _load_script_module(
        script_repo / "scripts" / "bootstrap_data_db.py",
        "bootstrap_data_db",
    )
    export_dependency_sources = _load_script_module(
        script_repo / "scripts" / "export_dependency_sources.py",
        "export_dependency_sources",
    )

    monkeypatch.setattr(bootstrap_data_db, "repo_root", lambda: repo_root)
    monkeypatch.setattr(export_dependency_sources, "repo_root", lambda: repo_root)

    assert bootstrap_data_db.main(["--data-dir", "data_db"]) == 0
    assert export_dependency_sources.main(["--data-dir", "data_db"]) == 0

    sources_json = repo_root / "docs" / "dependencies" / "sources.json"
    sources_md = repo_root / "docs" / "dependencies" / "sources.md"

    assert sources_json.exists()
    assert sources_md.exists()

    data = json.loads(sources_json.read_text(encoding="utf-8"))
    ids = [item["id"] for item in data.get("sources", [])]
    assert ids == ["a_dep", "b_dep"]

    md = sources_md.read_text(encoding="utf-8")
    assert "a_dep" in md
    assert "b_dep" in md
