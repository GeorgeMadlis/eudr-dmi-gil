# Dependency discovery, validation, and promotion (data_db-driven)

## Purpose

Track, validate, and promote dependency links deterministically without embedding upstream content in the repository.

## Data sources of truth

- `data_db/dependency_sources.csv` = current preferred links
- `data_db/dependency_link_history.csv` = observed candidates/history
- DuckDB tables `dependency_sources` + `dependency_link_history` (generated)

## Scripts

```sh
python scripts/bootstrap_data_db.py
python scripts/export_dependency_sources.py
python scripts/validate_dependency_links.py --fail-on-broken
python scripts/suggest_dependency_updates.py
python scripts/suggest_dependency_updates.py --promote-best
```

## Outputs (committed vs generated)

- `docs/dependencies/sources.json` + `docs/dependencies/sources.md` are generated and committed
- `out/dependency_link_check.json` and `out/dependency_update_suggestions.json` are generated and git-ignored
- raw downloaded datasets live under `data/` (git-ignored)

## Determinism / audit notes

- Stable ordering is enforced when writing JSON and CSV outputs.
- History CSV updates are idempotent (no duplicate rows on re-run).
- Optional `--no-timestamps` mode omits timestamps for deterministic snapshots.
