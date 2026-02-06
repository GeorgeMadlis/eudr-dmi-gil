# Repo-local data plane

This folder is the repo-local **data plane**.

It is intentionally **not committed to Git** and must not be published into the Digital Twin.
Only derived report bundles (under `EUDR_DMI_EVIDENCE_ROOT`) and the exported site bundle outputs
(e.g. `out/site_bundle/...`) are publishable.

## Layout

- `external/` — externally downloaded upstream datasets (e.g. Hansen tiles).
- `cache/` — HTTP caches / temporary downloads.
- `derived/` — intermediate products that are not meant for the evidence bundle.

## Notes

- Evidence bundles remain under `EUDR_DMI_EVIDENCE_ROOT` only.
- Do not commit anything under `data/`.
