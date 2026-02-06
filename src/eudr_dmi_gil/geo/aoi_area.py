from __future__ import annotations

import json
from pathlib import Path

from pyproj import Geod
from shapely.geometry import shape
from shapely.ops import unary_union


def _load_union_geometry(aoi_geojson_path: Path):
    data = json.loads(aoi_geojson_path.read_text(encoding="utf-8"))

    if data.get("type") == "FeatureCollection":
        geoms = [shape(feat["geometry"]) for feat in data.get("features", []) if feat.get("geometry")]
        if not geoms:
            raise ValueError("AOI GeoJSON FeatureCollection has no features")
        return unary_union(geoms)

    if data.get("type") == "Feature":
        return shape(data["geometry"])

    if data.get("type"):
        return shape(data)

    raise ValueError("Unsupported AOI GeoJSON")


def compute_aoi_geodesic_area_ha(aoi_geojson_path: Path) -> tuple[float, str]:
    """Compute AOI area in hectares using geodesic area on WGS84.

    Returns:
      (area_ha, method_string)
    """

    geom = _load_union_geometry(aoi_geojson_path)
    geod = Geod(ellps="WGS84")

    # pyproj.Geod.geometry_area_perimeter returns signed area in m^2.
    area_m2, _ = geod.geometry_area_perimeter(geom)
    area_ha = abs(float(area_m2)) / 10_000.0
    return area_ha, "geodesic_wgs84_pyproj"
