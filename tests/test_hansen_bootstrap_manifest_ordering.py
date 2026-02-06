from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from eudr_dmi_gil.deps import hansen_acquire
from eudr_dmi_gil.deps.hansen_bootstrap import ensure_hansen_for_aoi
from eudr_dmi_gil.reports.determinism import canonical_json_bytes


def _fake_urlopen_factory(payload: bytes):
    class _Response:
        def __init__(self, data: bytes) -> None:
            self._buf = io.BytesIO(data)

        def read(self, size: int = -1) -> bytes:
            return self._buf.read(size)

        def __enter__(self) -> "_Response":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    def _fake_urlopen(url: str):  # noqa: ANN001
        return _Response(payload)

    return _fake_urlopen


def _write_aoi_geojson(path: Path) -> None:
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [20.1, 50.1],
                            [20.9, 50.1],
                            [20.9, 50.9],
                            [20.1, 50.9],
                            [20.1, 50.1],
                        ]
                    ],
                },
            }
        ],
    }
    path.write_text(json.dumps(geojson), encoding="utf-8")


def test_hansen_bootstrap_manifest_ordering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("EUDR_DMI_DATA_ROOT", str(tmp_path))
    monkeypatch.delenv("EUDR_DMI_HANSEN_URL_TEMPLATE", raising=False)
    monkeypatch.setattr(
        hansen_acquire.urllib.request,
        "urlopen",
        _fake_urlopen_factory(b"tile-bytes"),
    )

    aoi_path = tmp_path / "aoi.geojson"
    _write_aoi_geojson(aoi_path)

    manifest_path = ensure_hansen_for_aoi(
        aoi_id="test_aoi",
        aoi_geojson_path=aoi_path,
        layers=["treecover2000", "lossyear"],
        download=True,
    )

    assert manifest_path.is_file()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert payload["aoi_id"] == "test_aoi"
    assert payload["dataset_version"] == hansen_acquire.DATASET_VERSION_DEFAULT
    assert payload["tile_ids"] == ["N50_E020"]
    assert payload["layers"] == ["lossyear", "treecover2000"]

    entries = payload["entries"]
    assert len(entries) == 2
    for entry in entries:
        assert set(entry.keys()) == {
            "tile_id",
            "layer",
            "local_path",
            "sha256",
            "size_bytes",
            "source_url",
            "status",
        }

    assert [entry["layer"] for entry in entries] == ["lossyear", "treecover2000"]

    file_bytes = manifest_path.read_bytes()
    assert file_bytes == canonical_json_bytes(payload) + b"\n"
