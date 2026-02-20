from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .schema import ReportV1


def _as_text(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    return str(value)


def render_report_pdf(report: ReportV1, output_path: str | Path) -> None:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(out), pagesize=A4, pageCompression=0, invariant=1)
    width, height = A4
    margin = 40
    y = height - margin

    def write_line(text: str, *, size: int = 10, step: int = 14, bold: bool = False) -> None:
        nonlocal y
        if y < margin:
            c.showPage()
            y = height - margin
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size)
        c.drawString(margin, y, text)
        y -= step

    payload = report.to_dict()

    write_line("EUDR Report V1", size=16, step=20, bold=True)
    write_line(f"Report ID: {payload['report_id']}")
    write_line(f"Run ID: {payload['run_id']}")
    write_line(f"Generated UTC: {payload['generated_at_utc']}")
    write_line("", step=8)

    write_line("Company data", bold=True)
    write_line(f"Operator: {_as_text(payload['company']['operator'])}")
    write_line(f"Address: {_as_text(payload['company']['address'])}")
    for key, value in payload["company"]["identifiers"].items():
        write_line(f"Identifier ({key}): {_as_text(value)}")
    write_line("", step=8)

    write_line("Commodity data", bold=True)
    write_line(f"Commodity type: {_as_text(payload['commodity']['commodity_type'])}")
    write_line(f"Country region label: {_as_text(payload['commodity']['country_region_label'])}")
    write_line(f"HS code: {_as_text(payload['commodity']['hs_code'])}")
    write_line(f"Volume: {_as_text(payload['commodity']['volume'])}")
    write_line(f"Country of production: {_as_text(payload['commodity']['country_of_production'])}")
    write_line("", step=8)

    write_line("Plot geolocation references", bold=True)
    for plot in payload["plots"]:
        write_line(
            f"{plot['plot_name']} | {plot['geojson_name']} | centroid=({plot['centroid_lat']}, {plot['centroid_lon']})"
        )
        write_line(
            f"area_ha={plot['area_ha']} ({plot['area_method']}) | polygon_count={plot['polygon_count']}"
        )
        for meta_key, meta_value in plot["metadata"].items():
            write_line(f"metadata.{meta_key}: {_as_text(meta_value)}")
    write_line("", step=8)

    assess = payload["deforestation_assessment"]
    write_line("Deforestation assessment", bold=True)
    write_line(f"Cutoff date: {assess['cutoff_date']}")
    write_line(f"Deforestation detected: {assess['deforestation_detected']}")
    if assess["evidence_maps"]:
        for item in assess["evidence_maps"]:
            write_line(f"Evidence map: {_as_text(item)}")
    else:
        write_line("Evidence map: N/A")
    for metric_key, metric_value in assess["summary_metrics"].items():
        write_line(f"{metric_key}: {_as_text(metric_value)}")
    write_line("", step=8)

    write_line(f"Risk level: {_as_text(payload['risk_level'])}", bold=True)
    write_line(f"Compliance readiness: {_as_text(payload['compliance_readiness'])}", bold=True)
    write_line("", step=8)

    write_line("Deterministic artifacts", bold=True)
    for artifact in payload["artifacts"]:
        write_line(f"- {artifact}")
    write_line(f"Manifest pointer: {payload['manifest_path']}")

    c.save()
