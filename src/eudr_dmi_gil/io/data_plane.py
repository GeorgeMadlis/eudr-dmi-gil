from __future__ import annotations

import os
import subprocess
from pathlib import Path


def repo_root() -> Path:
    """Return repository root.

    Preference order:
    1) `git rev-parse --show-toplevel` if available
    2) Walk parents from this file, looking for a repo marker
    """

    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return Path(out).resolve()
    except Exception:
        pass

    current = Path(__file__).resolve()
    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").is_file() and (parent / "src").is_dir():
            return parent
        if (parent / ".git").exists():
            return parent

    return current.parents[3]


def data_root() -> Path:
    """Repo-local data root.

    Defaults to <repo_root>/data and can be overridden via EUDR_DMI_DATA_ROOT.
    """

    override = os.environ.get("EUDR_DMI_DATA_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return (repo_root() / "data").resolve()


def external_root() -> Path:
    return data_root() / "external"


def cache_root() -> Path:
    return data_root() / "cache"


def derived_root() -> Path:
    return data_root() / "derived"


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def safe_relpath_under(root: str | Path, path: str | Path) -> str:
    """Return posix relpath if `path` is under `root`, else raise ValueError."""

    root_path = Path(root).resolve()
    target_path = Path(path).resolve()
    try:
        rel = target_path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError(f"Path is not under root: {target_path} not under {root_path}") from exc
    return rel.as_posix()
