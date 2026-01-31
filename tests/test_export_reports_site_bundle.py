from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from eudr_dmi_gil.reports.cli import main as aoi_cli_main
from eudr_dmi_gil.reports.site_bundle_export import ExportPaths, export_site_bundle_reports


def test_site_bundle_zip_sha256_deterministic(tmp_path: Path, monkeypatch) -> None:
    # Create a fixed evidence root and a fixed bundle on today's UTC date.
    evidence_root = tmp_path / "evidence"
    monkeypatch.setenv("EUDR_DMI_EVIDENCE_ROOT", str(evidence_root))

    bundle_id = "bundle-001"
    aoi_id = "aoi-123"

    # Generate a deterministic bundle (explicit bundle id, fixed metric rows ordering).
    rc = aoi_cli_main(
        [
            "--aoi-id",
            aoi_id,
            "--aoi-wkt",
            "POINT (0 0)",
            "--bundle-id",
            bundle_id,
            "--out-format",
            "both",
            "--metric",
            "b_metric=2:count:src:note b",
            "--metric",
            "a_metric=1:count:src:note a",
        ]
    )
    assert rc == 0

    bundle_date = datetime.now(timezone.utc).date()

    out_base = tmp_path / "docs"
    paths = ExportPaths(
        out_dir=out_base / "site_bundle_reports",
        zip_path=out_base / "site_bundle_reports.zip",
        zip_sha256_path=out_base / "site_bundle_reports.zip.sha256",
    )

    # Export twice; the zip should be identical.
    export_site_bundle_reports(
        evidence_root=evidence_root,
        start_date=bundle_date,
        end_date=bundle_date,
        paths=paths,
    )
    digest1 = paths.zip_sha256_path.read_text(encoding="utf-8")

    export_site_bundle_reports(
        evidence_root=evidence_root,
        start_date=bundle_date,
        end_date=bundle_date,
        paths=paths,
    )
    digest2 = paths.zip_sha256_path.read_text(encoding="utf-8")

    assert digest1 == digest2

    # Ensure index exists and is locally navigable.
    index = paths.out_dir / "index.html"
    assert index.exists()
    html = index.read_text(encoding="utf-8")
    assert "AOI Reports" in html

    # Ensure we actually copied the bundle.
    # Bundle path should be preserved within the portable folder.
    expected_bundle_dir = paths.out_dir / bundle_date.strftime("%Y-%m-%d") / bundle_id
    assert expected_bundle_dir.exists()
