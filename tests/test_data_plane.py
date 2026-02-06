from __future__ import annotations

from pathlib import Path

import pytest

from eudr_dmi_gil.io import data_plane


def test_data_root_defaults_to_repo_data(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EUDR_DMI_DATA_ROOT", raising=False)
    monkeypatch.setattr(data_plane, "repo_root", lambda: tmp_path)

    assert data_plane.data_root() == tmp_path / "data"


def test_data_root_override_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    override = tmp_path / "custom_data"
    monkeypatch.setenv("EUDR_DMI_DATA_ROOT", str(override))

    assert data_plane.data_root() == override


def test_subroots_under_data_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EUDR_DMI_DATA_ROOT", raising=False)
    monkeypatch.setattr(data_plane, "repo_root", lambda: tmp_path)

    dr = data_plane.data_root()
    assert data_plane.external_root().is_relative_to(dr)
    assert data_plane.cache_root().is_relative_to(dr)
    assert data_plane.derived_root().is_relative_to(dr)
