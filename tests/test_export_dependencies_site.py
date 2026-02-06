from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_export_dependencies_site(tmp_path: Path, monkeypatch) -> None:
    script_repo = Path(__file__).resolve().parents[1]
    exporter = _load_script_module(
        script_repo / "scripts" / "export_dependencies_site.py",
        "export_dependencies_site",
    )

    repo_root = tmp_path
    docs = repo_root / "docs" / "dependencies"
    docs.mkdir(parents=True, exist_ok=True)
    (docs / "flow.md").write_text("# Flow\n\n- Step A\n", encoding="utf-8")
    (docs / "sources.md").write_text("# Sources\n\nGenerated.\n", encoding="utf-8")

    monkeypatch.setattr(exporter, "repo_root", lambda: repo_root)

    assert exporter.main(["--docs-root", "docs"]) == 0

    site_deps = repo_root / "docs" / "site" / "dependencies"
    assert (site_deps / "flow.html").exists()
    assert (site_deps / "sources.html").exists()
    assert (site_deps / "index.html").exists()
