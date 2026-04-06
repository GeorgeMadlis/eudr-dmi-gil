# MCP Server Stubs — Data Source Registry

This directory contains MCP-compatible server stubs for every external data source consumed by the EUDR-DMI-GIL pipeline.

## Purpose

Each stub is the **canonical declaration** for one data source. It records:

- Source name and version
- Base URL (and URL template, if tile-based)
- Data format and acquisition contract
- Which pipeline components consume it (`used_by`)
- How to verify a download (checksum scheme)

These stubs are designed to be read and updated by AI agents. An agent that discovers a new data source, or that needs to update an existing source URL (e.g. because a provider changed their download path), should:

1. Read the relevant stub to understand the current contract
2. Update the `source_url`, `url_template`, or `dataset_version` field
3. Commit the change with a reference to the evidence that prompted the update

## Stubs

| File | Data source |
|------|-------------|
| `hansen_gfc.py` | Hansen Global Forest Change (GFC) — primary deforestation evidence |
| `maaamet_wfs.py` | Estonian Land Board (Maa-amet) WFS — cadastral parcel validation |

## Adding a new source

Copy one of the existing stubs as a template. The stub does not need to be a runnable MCP server — it is a structured declaration that the pipeline and AI agents can inspect.

Minimum required fields per stub:

```python
SOURCE_ID = "..."          # unique identifier
SOURCE_NAME = "..."        # human-readable name
SOURCE_URL = "..."         # base or canonical URL
DATASET_VERSION = "..."    # version string (update when provider releases new version)
DATA_FORMAT = "..."        # e.g. "GeoTIFF", "WFS/GML", "CSV"
USED_BY = [...]            # list of src/ module paths that consume this source
```
