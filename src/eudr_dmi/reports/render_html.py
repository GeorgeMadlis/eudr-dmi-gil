from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .io import write_text
from .schema import ReportV1


def render_report_html(report: ReportV1, output_path: str | Path) -> None:
    template_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report_v1.html.j2")

    html = template.render(report=report.to_dict())
    write_text(output_path, html)
