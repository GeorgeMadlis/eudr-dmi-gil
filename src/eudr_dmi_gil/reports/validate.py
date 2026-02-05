from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import jsonschema
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError


def _find_repo_root(start: Path) -> Path:
    current = start
    for _ in range(10):
        if (current / "pyproject.toml").exists() and (current / "schemas").exists():
            return current
        if current.parent == current:
            break
        current = current.parent
    raise RuntimeError("Could not locate repo root (pyproject.toml + schemas/) from: " + str(start))


def _default_schema_path() -> Path:
    repo_root = _find_repo_root(Path(__file__).resolve())
    return repo_root / "schemas" / "reports" / "aoi_report_v1.schema.json"


def load_schema(schema_path: str | Path | None = None) -> dict[str, Any]:
    path = Path(schema_path) if schema_path is not None else _default_schema_path()
    return json.loads(path.read_text(encoding="utf-8"))


def validate_aoi_report_v1(
    report: Mapping[str, Any],
    *,
    schema_path: str | Path | None = None,
) -> None:
    """Validate an AOI report JSON object against the AOI report v1 schema.

    Raises:
      jsonschema.exceptions.ValidationError if invalid.
    """

    schema = load_schema(schema_path)
    validator = Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    validator.validate(dict(report))

    _validate_traceability(dict(report))


def _validate_traceability(report: Mapping[str, Any]) -> None:
    evidence_classes = {
        item.get("class_id")
        for item in report.get("evidence_registry", {}).get("evidence_classes", [])
        if isinstance(item, Mapping)
    }
    acceptance_criteria = {
        item.get("criteria_id")
        for item in report.get("acceptance_criteria", [])
        if isinstance(item, Mapping)
    }
    results = {
        item.get("result_id")
        for item in report.get("results", [])
        if isinstance(item, Mapping)
    }

    traceability = report.get("regulatory_traceability", [])

    referenced_results: set[str] = set()
    for entry in traceability:
        if not isinstance(entry, Mapping):
            continue
        evidence_class = entry.get("evidence_class")
        criteria_id = entry.get("acceptance_criteria")
        result_ref = entry.get("result_ref")

        if evidence_class and evidence_class not in evidence_classes:
            raise ValidationError(
                f"Traceability references unknown evidence_class: {evidence_class}"
            )
        if criteria_id and criteria_id not in acceptance_criteria:
            raise ValidationError(
                f"Traceability references unknown acceptance_criteria: {criteria_id}"
            )
        if result_ref and result_ref not in results:
            raise ValidationError(
                f"Traceability references unknown result_ref: {result_ref}"
            )
        if isinstance(result_ref, str):
            referenced_results.add(result_ref)

    orphaned_results = sorted(r for r in results if r not in referenced_results)
    if orphaned_results:
        raise ValidationError(f"Orphaned results without traceability: {orphaned_results}")


def validate_aoi_report_v1_file(
    json_path: str | Path,
    *,
    schema_path: str | Path | None = None,
) -> dict[str, Any]:
    """Load and validate a report JSON file; returns the parsed JSON."""

    obj = json.loads(Path(json_path).read_text(encoding="utf-8"))
    validate_aoi_report_v1(obj, schema_path=schema_path)
    return obj
