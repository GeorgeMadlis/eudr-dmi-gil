# Inspection Index (Authoritative Implementation)

## Authority boundary

This repository is the authoritative implementation for EUDR-DMI-GIL. The Digital Twin repository is the public, non-authoritative portal for inspection and governance.

## Workspace Bootstrap

- Open scripts/eudr-dmi-gil.code-workspace.
- Re-run Prompt 0: Workspace Bootstrap.
- All changes must be tested via scripts/run_example_report_clean.sh.

## Governance and DAO Context

DAO proposals are produced via the DTE workflow and must be grounded in the Digital Twin inspection surface.

- Digital Twin DTE Instructions (Canonical): https://github.com/georgemadlis/eudr-dmi-gil-digital-twin/blob/main/docs/dte_instructions.md

All implementation changes should be traceable back to a DAO proposal grounded via the DTE workflow.

## Architecture

- [docs/architecture/decision_records/0001-report-pipeline-architecture.md](architecture/decision_records/0001-report-pipeline-architecture.md)
- [docs/architecture/dependency_register.md](architecture/dependency_register.md)

## Dependencies

- [docs/dependencies/README.md](dependencies/README.md)
- [docs/dependencies/sources.md](dependencies/sources.md)

## Reports

- [docs/reports/README.md](reports/README.md)
- [docs/reports/runbook_generate_aoi_report.md](reports/runbook_generate_aoi_report.md)

## Operations

- [docs/operations/environment_setup.md](operations/environment_setup.md)
- [docs/operations/minio_setup.md](operations/minio_setup.md)
- [docs/operations/migration_runbook.md](operations/migration_runbook.md)

## Schemas (Output Contracts)

These JSON schemas are the authoritative contracts for all published artefacts.

- [schemas/reports/aoi_report_v2.schema.json](../schemas/reports/aoi_report_v2.schema.json)
- [schemas/reports/bundle_manifest_v1.schema.json](../schemas/reports/bundle_manifest_v1.schema.json)
- [schemas/reports/site_bundle_v1.schema.json](../schemas/reports/site_bundle_v1.schema.json)

## Developer Onboarding

- [CLAUDE.md](../CLAUDE.md) — primary onboarding guide for developers and AI agents; covers commands, architecture, publish flow, and evidence integrity rules.

## CI Workflows

- [.github/workflows/pr-checks.yml](../.github/workflows/pr-checks.yml) — runs tests and lint on every pull request
- [.github/workflows/check-dt-freshness.yml](../.github/workflows/check-dt-freshness.yml) — daily workflow that regenerates the example AOI bundle and compares it to the published Digital Twin content; fails if the DT is stale

## Data Source Registry (MCP Servers)

The `src/mcp_servers/` directory contains MCP-compatible server stubs for each external data source consumed by the pipeline. Each stub declares the source URL, expected data format, and the acquisition contract. These stubs are the canonical entry points for agents discovering or updating data source links.

- [src/mcp_servers/](../src/mcp_servers/) — one module per data source (Hansen GFC, Maa-amet WFS, etc.)
