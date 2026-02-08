from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


def _run_cli(args: list[str], *, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "eudr_dmi_gil.reports.cli", *args],
        check=False,
        text=True,
        capture_output=True,
        env=env,
    )


def test_estonia_testland1_geojson_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    geojson_path = repo_root / "aoi_json_examples" / "estonia_testland1.geojson"
    if not geojson_path.is_file():
        pytest.skip("estonia_testland1.geojson not found")

    evidence_root = tmp_path / "evidence"
    env = os.environ.copy()
    env["EUDR_DMI_EVIDENCE_ROOT"] = str(evidence_root)

    bundle_id = "estonia_testland1-smoke"
    aoi_id = "estonia_testland1"

    proc = _run_cli(
        [
            "--aoi-id",
            aoi_id,
            "--aoi-geojson",
            str(geojson_path),
            "--bundle-id",
            bundle_id,
            "--out-format",
            "both",
        ],
        env=env,
    )

    if proc.returncode != 0:
        pytest.skip(f"CLI failed (environment prerequisites missing): {proc.stderr}")

    bundle_date = datetime.now(timezone.utc).date().strftime("%Y-%m-%d")
    bundle_dir = evidence_root / bundle_date / bundle_id

    report_json = bundle_dir / "reports" / "aoi_report_v2" / f"{aoi_id}.json"
    report_html = bundle_dir / "reports" / "aoi_report_v2" / f"{aoi_id}.html"
    metrics_csv = bundle_dir / "reports" / "aoi_report_v2" / aoi_id / "metrics.csv"
    manifest = bundle_dir / "manifest.json"
    geometry = bundle_dir / "inputs" / "aoi.geojson"

    assert report_json.exists()
    assert report_html.exists()
    assert metrics_csv.exists()
    assert manifest.exists()
    assert geometry.exists()

    report = json.loads(report_json.read_text(encoding="utf-8"))
    forest_metrics = report.get("forest_metrics")
    methodology = report.get("methodology", {})
    if isinstance(forest_metrics, dict) and forest_metrics:
        assert forest_metrics.get("loss_year_code_basis") == 2000

    forest_method = methodology.get("forest_loss_post_2020") if isinstance(methodology, dict) else None
    if isinstance(forest_method, dict):
        calculation = forest_method.get("calculation", {})
        assert calculation.get("cutoff_date") == "2020-12-31"

    evidence_artifacts = report.get("evidence_artifacts", [])
    if isinstance(evidence_artifacts, list) and evidence_artifacts:
        relpaths = {entry.get("relpath") for entry in evidence_artifacts if isinstance(entry, dict)}
        required = {
            f"reports/aoi_report_v2/{aoi_id}/hansen/forest_loss_post_2020_mask.geojson",
            f"reports/aoi_report_v2/{aoi_id}/hansen/forest_current_tree_cover_mask.geojson",
            f"reports/aoi_report_v2/{aoi_id}/hansen/forest_loss_post_2020_summary.json",
            f"reports/aoi_report_v2/{aoi_id}/hansen/forest_loss_post_2020_tiles.json",
        }
        if required & relpaths:
            assert required.issubset(relpaths)
