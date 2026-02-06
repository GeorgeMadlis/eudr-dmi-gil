#!/usr/bin/env python3
"""Export dependency docs to a lightweight HTML site bundle."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def ensure_repo_relative(path: Path, *, label: str) -> None:
    if path.is_absolute():
        raise ValueError(f"{label} must be repo-relative (no absolute paths): {path}")


def resolve_under_repo(rel: Path) -> Path:
    root = repo_root().resolve()
    resolved = (root / rel).resolve()
    if root not in resolved.parents and resolved != root:
        raise ValueError(f"Path escapes repo root: {rel} -> {resolved}")
    return resolved


def _render_markdown_basic(text: str) -> str:
    lines = text.splitlines()
    html_lines: list[str] = []
    in_code = False
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip().startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                close_list()
                html_lines.append("<pre><code>")
                in_code = True
            continue

        if in_code:
            html_lines.append(html.escape(line))
            continue

        if line.startswith("# "):
            close_list()
            html_lines.append(f"<h1>{html.escape(line[2:].strip())}</h1>")
            continue
        if line.startswith("## "):
            close_list()
            html_lines.append(f"<h2>{html.escape(line[3:].strip())}</h2>")
            continue
        if line.startswith("### "):
            close_list()
            html_lines.append(f"<h3>{html.escape(line[4:].strip())}</h3>")
            continue

        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(line[2:].strip())}</li>")
            continue

        if not line.strip():
            close_list()
            html_lines.append("<p></p>")
            continue

        close_list()
        html_lines.append(f"<p>{html.escape(line.strip())}</p>")

    close_list()
    if in_code:
        html_lines.append("</code></pre>")

    return "\n".join(html_lines)


def _wrap_html(title: str, body_html: str, *, nav_html: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial; margin: 24px; }}
    nav a {{ margin-right: 12px; }}
    pre {{ background: #f6f6f6; padding: 12px; overflow-x: auto; }}
    code {{ background: #f6f6f6; padding: 1px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <nav>{nav_html}</nav>
  {body_html}
</body>
</html>
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export dependency docs to HTML")
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Repo-relative docs root (default: docs)",
    )
    args = parser.parse_args(argv)

    try:
        docs_root_rel = Path(args.docs_root)
        ensure_repo_relative(docs_root_rel, label="--docs-root")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 2

    docs_root = resolve_under_repo(docs_root_rel)
    deps_dir = docs_root / "dependencies"
    site_deps_dir = docs_root / "site" / "dependencies"
    site_deps_dir.mkdir(parents=True, exist_ok=True)

    flow_md = deps_dir / "flow.md"
    sources_md = deps_dir / "sources.md"

    if not flow_md.exists() or not sources_md.exists():
        missing = []
        if not flow_md.exists():
            missing.append(str(flow_md))
        if not sources_md.exists():
            missing.append(str(sources_md))
        print(f"ERROR: missing markdown files: {', '.join(missing)}")
        return 2

    nav_html = (
        '<a href="index.html">Dependencies</a>'
        '<a href="flow.html">Dependency flow</a>'
        '<a href="sources.html">Dependency sources</a>'
    )

    flow_html = _wrap_html("Dependency flow", _render_markdown_basic(flow_md.read_text(encoding="utf-8")), nav_html=nav_html)
    sources_html = _wrap_html(
        "Dependency sources",
        _render_markdown_basic(sources_md.read_text(encoding="utf-8")),
        nav_html=nav_html,
    )

    (site_deps_dir / "flow.html").write_text(flow_html, encoding="utf-8")
    (site_deps_dir / "sources.html").write_text(sources_html, encoding="utf-8")

    index_html = _wrap_html(
        "Dependencies",
        """
<h1>Dependencies</h1>
<ul>
  <li><a href=\"flow.html\">Dependency flow (how links are discovered/promoted)</a></li>
  <li><a href=\"sources.html\">Dependency sources (generated registry)</a></li>
</ul>
""",
        nav_html=nav_html,
    )
    (site_deps_dir / "index.html").write_text(index_html, encoding="utf-8")

    print(str(site_deps_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
