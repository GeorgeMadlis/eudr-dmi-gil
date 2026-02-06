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
    assert data_plane.cache_root().is_relative_to(dr)
    assert data_plane.derived_root().is_relative_to(dr)


def test_external_root_default(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EUDR_DMI_DATA_ROOT", raising=False)
    monkeypatch.setattr(data_plane, "DEFAULT_EXTERNAL_ROOT", tmp_path / "external_root")

    ext_root = data_plane.external_root()
    assert ext_root == tmp_path / "external_root"
    assert ext_root.is_dir()


def test_external_dataset_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("EUDR_DMI_DATA_ROOT", raising=False)
    monkeypatch.setattr(data_plane, "DEFAULT_EXTERNAL_ROOT", tmp_path / "external_root")

    dataset_dir = data_plane.external_dataset_dir("hansen", "2024-v1.12")
    assert dataset_dir == tmp_path / "external_root" / "datasets" / "hansen" / "2024-v1.12"
    assert dataset_dir.is_dir()
