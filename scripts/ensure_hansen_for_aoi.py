#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eudr_dmi_gil.deps.hansen_bootstrap import (
    ensure_hansen_for_aoi,
    hansen_tiles_root,
)
from eudr_dmi_gil.io import data_plane


def _parse_layers(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure Hansen tiles are available for a given AOI"
    )
    parser.add_argument("--aoi-id", required=True)
    parser.add_argument("--aoi-geojson", required=True)
    parser.add_argument(
        "--download",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Download missing tiles (default: true)",
    )
    parser.add_argument(
        "--layers",
        default="treecover2000,lossyear",
        help="Comma-separated list of layers to ensure",
    )
    parser.add_argument(
        "--minio-cache",
        action="store_true",
        help="Enable MinIO cache for tiles and manifest",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Disable HTTP downloads (use local/minio only)",
    )
    parser.add_argument(
        "--print-paths",
        action="store_true",
        help="Print resolved external root and tiles directory",
    )

    args = parser.parse_args()

    try:
        manifest_path = ensure_hansen_for_aoi(
            aoi_id=args.aoi_id,
            aoi_geojson_path=Path(args.aoi_geojson),
            layers=_parse_layers(args.layers),
            download=args.download,
            minio_cache_enabled=args.minio_cache,
            offline=args.offline,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.print_paths:
        print(f"external_root={data_plane.external_root()}")
        print(f"hansen_tiles_root={hansen_tiles_root()}")
    print(f"manifest_path={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
