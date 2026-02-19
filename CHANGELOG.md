# Changelog

## 2026-02-19

### AOI reports link + forest layer alignment

- eudr-dmi-gil — 165556f
  - Updated report map layer wiring so `forest_end_year` points to the current forest mask, preventing visual overlap confusion with post-2020 loss.
- eudr-client-portal — 48b5891
  - Updated Dashboard "DAO Reports" link to open AOI reports index instead of the example run report.
- eudr-dmi-gil-digital-twin — add372d
  - Regenerated 4 AOI report runs (example, latin_america, se_asia, west_africa) with updated map configs and synchronized report artifacts.
