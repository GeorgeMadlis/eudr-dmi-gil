from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


NA_VALUE = "N/A"


def na_if_missing(value: Any) -> Any:
    if value is None:
        return NA_VALUE
    if isinstance(value, str) and not value.strip():
        return NA_VALUE
    return value


def na_dict(values: dict[str, Any] | None, keys: list[str]) -> dict[str, Any]:
    source = values or {}
    return {key: na_if_missing(source.get(key)) for key in keys}


@dataclass(frozen=True)
class CompanyData:
    operator: str
    address: str
    identifiers: dict[str, Any]


@dataclass(frozen=True)
class CommodityData:
    commodity_type: str
    country_region_label: str
    hs_code: str
    volume: Any
    country_of_production: str


@dataclass(frozen=True)
class PlotReference:
    plot_name: str
    geojson_name: str
    centroid_lat: float
    centroid_lon: float
    area_ha: float
    area_method: str
    polygon_count: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DeforestationAssessment:
    cutoff_date: str
    deforestation_detected: str
    evidence_maps: list[str]
    summary_metrics: dict[str, Any]


@dataclass(frozen=True)
class ReportV1:
    report_version: str
    report_id: str
    run_id: str
    plot_id: str
    generated_at_utc: str
    data_sources_summary: list[str]
    company: CompanyData
    commodity: CommodityData
    plots: list[PlotReference]
    deforestation_assessment: DeforestationAssessment
    risk_level: str
    compliance_readiness: str
    artifacts: list[str]
    manifest_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
