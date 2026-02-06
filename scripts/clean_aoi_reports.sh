#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TARGETS=(
  "$ROOT_DIR/out/aoi_reports"
  "$ROOT_DIR/out/site_bundle/aoi_reports"
)

echo "==> Cleaning AOI report outputs"

for dir in "${TARGETS[@]}"; do
  if [[ -d "$dir" ]]; then
    echo " - removing $dir"
    rm -rf "$dir"
  else
    echo " - skip (not present): $dir"
  fi
done

echo "==> AOI report outputs cleaned"
