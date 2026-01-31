from __future__ import annotations

import argparse
import shutil
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from .bundle import resolve_evidence_root
from .determinism import create_deterministic_zip, sha256_file, write_bytes


@dataclass(frozen=True)
class ExportPaths:
    out_dir: Path
    zip_path: Path
    zip_sha256_path: Path


def _parse_yyyy_mm_dd(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as e:
        raise argparse.ArgumentTypeError("Expected YYYY-MM-DD") from e


def _iter_dates(start: date, end: date) -> list[date]:
    if end < start:
        raise ValueError("end date must be >= start date")

    days = (end - start).days
    return [start.fromordinal(start.toordinal() + i) for i in range(days + 1)]


def _copy_bundle_into_site_root(
    *,
    bundle_src: Path,
    site_root: Path,
    rel_bundle_root: Path,
) -> Path:
    dest = site_root / rel_bundle_root
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(bundle_src, dest)
    return dest


def _find_aoi_report_html_paths(bundle_root: Path) -> list[Path]:
    p = bundle_root / "reports" / "aoi_report_v1"
    if not p.exists():
        return []
    return sorted(p.glob("*.html"), key=lambda x: x.as_posix())


def _render_index_html(entries: list[tuple[str, str, str]]) -> str:
    rows = "\n".join(
        f"<tr><td><code>{d}</code></td><td><code>{bid}</code></td><td><a href=\"{href}\">open</a></td></tr>"
        for d, bid, href in entries
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AOI Reports (Portable Bundle)</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 24px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f6f6f6; text-align: left; }}
    code {{ background: #f6f6f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>AOI Reports</h1>
  <p>Portable site bundle generated from evidence bundles.</p>
  <table>
    <thead>
      <tr><th>Date</th><th>Bundle</th><th>Report</th></tr>
    </thead>
    <tbody>
      {rows or '<tr><td colspan="3">No reports found.</td></tr>'}
    </tbody>
  </table>
</body>
</html>
"""


def export_site_bundle_reports(
    *,
    evidence_root: Path,
    start_date: date,
    end_date: date,
    paths: ExportPaths,
) -> None:
    if paths.out_dir.exists():
        shutil.rmtree(paths.out_dir)
    paths.out_dir.mkdir(parents=True, exist_ok=True)

    entries: list[tuple[str, str, str]] = []

    for d in _iter_dates(start_date, end_date):
        d_str = d.strftime("%Y-%m-%d")
        date_root = evidence_root / d_str
        if not date_root.exists():
            continue

        for bundle_src in sorted(date_root.iterdir(), key=lambda p: p.name):
            if not bundle_src.is_dir():
                continue

            rel_bundle_root = Path(d_str) / bundle_src.name
            bundle_dest = _copy_bundle_into_site_root(
                bundle_src=bundle_src,
                site_root=paths.out_dir,
                rel_bundle_root=rel_bundle_root,
            )

            for html_path in _find_aoi_report_html_paths(bundle_dest):
                rel_href = html_path.relative_to(paths.out_dir).as_posix()
                entries.append((d_str, bundle_src.name, rel_href))

    entries_sorted = sorted(entries, key=lambda e: (e[0], e[1], e[2]))

    index_path = paths.out_dir / "index.html"
    index_path.write_text(_render_index_html(entries_sorted), encoding="utf-8")

    prefix = "site_bundle_reports/"
    files: dict[str, bytes] = {}
    for p in sorted(paths.out_dir.rglob("*"), key=lambda x: x.as_posix()):
        if p.is_dir():
            continue
        rel = p.relative_to(paths.out_dir).as_posix()
        files[prefix + rel] = p.read_bytes()

    create_deterministic_zip(paths.zip_path, files)

    digest = sha256_file(paths.zip_path)
    write_bytes(paths.zip_sha256_path, f"{digest}  {paths.zip_path.name}\n".encode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m eudr_dmi_gil.reports.site_bundle_export",
        description=(
            "Build a portable HTML site bundle for AOI reports under the evidence root, for a date or date range."
        ),
    )

    p.add_argument(
        "--evidence-root",
        help="Evidence root override. If omitted uses EUDR_DMI_EVIDENCE_ROOT or audit/evidence/.",
    )

    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--date", type=_parse_yyyy_mm_dd, help="Single UTC date YYYY-MM-DD")
    g.add_argument("--range", nargs=2, metavar=("START", "END"), type=_parse_yyyy_mm_dd)

    p.add_argument(
        "--out-base",
        default="docs",
        help="Base output directory (default: docs).",
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    evidence_root = resolve_evidence_root(args.evidence_root)

    if args.date:
        start = end = args.date
    else:
        start, end = args.range

    out_base = Path(args.out_base)
    paths = ExportPaths(
        out_dir=out_base / "site_bundle_reports",
        zip_path=out_base / "site_bundle_reports.zip",
        zip_sha256_path=out_base / "site_bundle_reports.zip.sha256",
    )

    export_site_bundle_reports(
        evidence_root=evidence_root,
        start_date=start,
        end_date=end,
        paths=paths,
    )

    print(str(paths.out_dir))
    print(str(paths.zip_path))
    print(str(paths.zip_sha256_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
