"""Hansen Global Forest Change (GFC) — data source stub.

This module is the canonical declaration of the Hansen GFC acquisition
contract. AI agents that discover a new dataset version or a changed
download URL should update the fields below and commit the change.

Do NOT run this module directly. Pipeline acquisition logic lives in:
  src/eudr_dmi_gil/deps/hansen_acquire.py
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Source identity
# ---------------------------------------------------------------------------

SOURCE_ID = "hansen_gfc"
SOURCE_NAME = "Hansen Global Forest Change (GFC)"
PROVIDER = "Google / Hansen et al."
DATASET_VERSION = "2024-v1.12"  # Update this when a new annual release is available

# ---------------------------------------------------------------------------
# Download contract
# ---------------------------------------------------------------------------

# Base storage bucket (Google Cloud Storage, public)
SOURCE_URL = "https://storage.googleapis.com/earthenginepartners-hansen/"

# Tile URL template — {layer} and {url_tile_id} are substituted per tile
URL_TEMPLATE = (
    "https://storage.googleapis.com/earthenginepartners-hansen/"
    "GFC-2024-v1.12/Hansen_GFC-2024-v1.12_{layer}_{url_tile_id}.tif"
)

DATA_FORMAT = "GeoTIFF"
TILE_GRID = "10x10-degree latitude/longitude tiles"
CHECKSUM_SCHEME = "SHA-256 per tile file"

# ---------------------------------------------------------------------------
# Pipeline consumers
# ---------------------------------------------------------------------------

USED_BY = [
    "src/eudr_dmi_gil/deps/hansen_acquire.py",
    "src/eudr_dmi_gil/deps/hansen_tiles.py",
    "src/eudr_dmi_gil/deps/minio_cache.py",
]

# ---------------------------------------------------------------------------
# Layers acquired
# ---------------------------------------------------------------------------

LAYERS = [
    "treecover2000",   # Percentage tree cover in year 2000
    "lossyear",        # Year of forest loss (0 = no loss, 1–24 = year 2001–2024)
    "gain",            # Forest gain 2000–2012 (binary)
    "datamask",        # Data quality mask
]

# ---------------------------------------------------------------------------
# Agent instructions
# ---------------------------------------------------------------------------

AGENT_NOTES = """
To update this source when a new Hansen annual release is published:

1. Update DATASET_VERSION (e.g. "2025-v1.13")
2. Update URL_TEMPLATE to match the new release path
3. Run the regression test to verify tile acquisition still works:
     bash scripts/run_example_report_clean.sh
4. Commit this file with a reference to the Hansen release announcement.

The environment variable EUDR_DMI_HANSEN_URL_TEMPLATE overrides URL_TEMPLATE
at runtime (set in .env or Docker Compose) and takes precedence over this stub.
"""
