"""Estonian Land Board (Maa-amet) WFS — data source stub.

This module is the canonical declaration of the Maa-amet WFS acquisition
contract. AI agents that need to update the service URL, layer name, or
data format should edit the fields below and commit the change.

Do NOT run this module directly. Pipeline acquisition logic lives in:
  src/eudr_dmi_gil/analysis/maaamet_validation.py
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Source identity
# ---------------------------------------------------------------------------

SOURCE_ID = "maaamet_wfs"
SOURCE_NAME = "Estonian Land Board (Maa-amet) — Cadastral WFS"
PROVIDER = "Maa-amet / Estonian Land Board"
DATASET_VERSION = "live"  # Real-time WFS; no versioned snapshots

# ---------------------------------------------------------------------------
# Download contract
# ---------------------------------------------------------------------------

# Base WFS endpoint (set via MAAAMET_WFS_URL env var at runtime)
# The actual URL is deployment-specific and must be configured in .env.
# Agents updating this source should discover the current public endpoint
# from the Maa-amet INSPIRE portal: https://inspire.maaamet.ee/
SOURCE_URL = "https://inspire.maaamet.ee/"  # Discovery URL; runtime endpoint in MAAAMET_WFS_URL

# Default WFS layer for cadastral parcel validation
DEFAULT_LAYER = "kataster:ky_kehtiv"

DATA_FORMAT = "WFS/GML (OGC Web Feature Service)"
CHECKSUM_SCHEME = "None — live service; results are not checksummed per request"

# ---------------------------------------------------------------------------
# Pipeline consumers
# ---------------------------------------------------------------------------

USED_BY = [
    "src/eudr_dmi_gil/analysis/maaamet_validation.py",
    "src/eudr_dmi_gil/reports/cli.py",
]

# ---------------------------------------------------------------------------
# Runtime environment variables
# ---------------------------------------------------------------------------

ENV_VARS = {
    "MAAAMET_WFS_URL": "WFS service base URL (required to enable Maa-amet validation)",
    "MAAAMET_WFS_LAYER": f"WFS layer name (default: {DEFAULT_LAYER!r})",
    "EUDR_DMI_MAAAMET_WFS_TIMEOUT": "Request timeout in seconds (default: 60)",
}

# ---------------------------------------------------------------------------
# Agent instructions
# ---------------------------------------------------------------------------

AGENT_NOTES = """
Maa-amet does not version their WFS snapshots. The service URL may change
when Maa-amet updates their INSPIRE infrastructure.

To update this source when the WFS endpoint changes:

1. Discover the new endpoint from https://inspire.maaamet.ee/ (INSPIRE portal)
2. Update SOURCE_URL with the new discovery URL
3. Update ENV_VARS["MAAAMET_WFS_URL"] description with the new endpoint hint
4. Update .env.example and docs/operations/environment_setup.md with the new URL
5. Run the regression test to verify WFS queries still work:
     MAAAMET_WFS_URL=<new-url> bash scripts/run_example_report_clean.sh
6. Commit this file with a reference to the Maa-amet announcement or INSPIRE discovery.

Note: Maa-amet validation is gated by AOI region — it only runs when the AOI
overlaps with Estonian cadastral data.
"""
