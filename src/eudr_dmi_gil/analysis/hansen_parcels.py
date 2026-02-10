from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import rasterio
from rasterio.warp import transform_geom

from eudr_dmi_gil.geo.forest_area_core import (
    forest_mask_end_year,
    pixel_area_m2_raster,
    rasterize_zone_mask,
)
from eudr_dmi_gil.tasks.forest_loss_post_2020_clean import LocalTileSource, _pair_tiles


@dataclass(frozen=True)
class HansenParcelStats:
    parcel_id: str
    hansen_land_area_ha: float
    hansen_forest_area_ha: float


def compute_hansen_parcel_stats(
    *,
    parcels: Iterable[object],
    tile_dir: Path,
    canopy_threshold_percent: int,
    end_year: int,
) -> dict[str, HansenParcelStats]:
    """Compute Hansen-based land/forest area for parcel geometries.

    Expects each parcel to expose `parcel_id` and `geometry` attributes.
    """

    parcel_list = [p for p in parcels if getattr(p, "geometry", None)]
    if not parcel_list:
        return {}

    stats: dict[str, HansenParcelStats] = {
        p.parcel_id: HansenParcelStats(
            parcel_id=p.parcel_id,
            hansen_land_area_ha=0.0,
            hansen_forest_area_ha=0.0,
        )
        for p in parcel_list
    }

    tile_source = LocalTileSource(tile_dir)
    treecover_tiles = tile_source.list_layer_files("treecover2000")
    lossyear_tiles = tile_source.list_layer_files("lossyear")
    pairs = _pair_tiles(treecover_tiles, lossyear_tiles)

    for tree_path, loss_path in pairs:
        with rasterio.open(tree_path) as tree_ds, rasterio.open(loss_path) as loss_ds:
            tree_band = tree_ds.read(1, masked=True)
            loss_band = loss_ds.read(1, masked=True)

            if tree_band.shape != loss_band.shape:
                raise RuntimeError("Mismatched raster shapes for treecover2000 and lossyear")

            valid = (~tree_band.mask) & (~loss_band.mask)
            tree_values = np.ma.filled(tree_band, 0)
            loss_values = np.ma.filled(loss_band, 0)

            forest_end_mask = forest_mask_end_year(
                tree_values,
                loss_values,
                canopy_threshold_percent,
                end_year,
            ) & valid

            pixel_area_m2 = pixel_area_m2_raster(
                tree_ds.transform,
                height=tree_band.shape[0],
                width=tree_band.shape[1],
                crs=tree_ds.crs,
            )

            for parcel in parcel_list:
                parcel_geom = transform_geom("EPSG:4326", tree_ds.crs, parcel.geometry)
                zone_mask = rasterize_zone_mask(
                    parcel_geom,
                    out_shape=tree_band.shape,
                    transform=tree_ds.transform,
                    all_touched=True,
                )

                zone_valid = zone_mask & valid
                if not np.any(zone_valid):
                    continue

                land_area_ha = float(np.sum(pixel_area_m2[zone_valid], dtype=np.float64)) / 10_000.0
                forest_area_ha = (
                    float(np.sum(pixel_area_m2[forest_end_mask & zone_mask], dtype=np.float64))
                    / 10_000.0
                )

                current = stats[parcel.parcel_id]
                stats[parcel.parcel_id] = HansenParcelStats(
                    parcel_id=parcel.parcel_id,
                    hansen_land_area_ha=current.hansen_land_area_ha + land_area_ha,
                    hansen_forest_area_ha=current.hansen_forest_area_ha + forest_area_ha,
                )

    return stats
