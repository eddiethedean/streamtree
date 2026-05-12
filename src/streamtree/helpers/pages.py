"""Multipage discovery helpers (stdlib + pathlib).

Streamlit serves extra views from a ``pages/`` directory next to the main script
(see Streamlit multipage apps). These helpers **enumerate** ``*.py`` page files
and derive **sort order** and **human labels** from filenames so you can build
``PageLink`` / ``Routes`` metadata without hard-coding paths.

This module does **not** start a second server or import page modules; it only
inspects the filesystem.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

# Leading digits + underscore(s), rest is title segments separated by underscores.
_ORDERED_STEM = re.compile(r"^(\d+)_(.+)$")


@dataclass(frozen=True)
class PageEntry:
    """One ``pages/*.py`` file discovered on disk.

    Attributes:
        path: Absolute path to the page script.
        stem: Filename without ``.py`` (e.g. ``01_Getting_started``).
        sort_key: Tuple ``(order, stem)`` for stable ordering (lower ``order`` first).
        label: Title derived for UI (underscores → spaces; leading order stripped).
        page: Relative path suitable for :class:`streamtree.elements.widgets.PageLink`
            ``page=`` (POSIX-style, e.g. ``pages/1_Hello.py``).
    """

    path: Path
    stem: str
    sort_key: tuple[int, str]
    label: str
    page: str


def pages_dir_next_to(main_script: str | Path) -> Path:
    """Return the ``pages`` directory path next to ``main_script`` (may not exist).

    ``main_script`` should be the path to your entry ``.py`` file (often ``__file__``).
    """
    p = Path(main_script).expanduser().resolve()
    return p.parent / "pages"


def list_page_entries(pages_dir: str | Path) -> list[PageEntry]:
    """List discoverable page scripts under ``pages_dir``, sorted like Streamlit sidebar.

    Skips non-``.py`` files, ``__init__.py``, and names starting with ``_`` (Streamlit
    ignores underscore-prefixed page files).
    """
    root = Path(pages_dir).expanduser().resolve()
    if not root.is_dir():
        return []

    project_root = root.parent

    entries: list[PageEntry] = []
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.suffix != ".py":
            continue
        stem = path.stem
        if stem.startswith("_") or stem == "__init__":
            continue
        m = _ORDERED_STEM.match(stem)
        if m:
            order = int(m.group(1))
            title_part = m.group(2)
        else:
            # Unnumbered pages sort after numbered ones (large sentinel order).
            order = 1_000_000
            title_part = stem
        label = title_part.replace("_", " ").strip() or stem
        rel = path.resolve().relative_to(project_root.resolve())
        page = rel.as_posix()
        entries.append(
            PageEntry(
                path=path.resolve(),
                stem=stem,
                sort_key=(order, stem.lower()),
                label=label,
                page=page,
            )
        )

    entries.sort(key=lambda e: e.sort_key)
    return entries


def discover_pages(main_script: str | Path) -> list[PageEntry]:
    """Discover pages next to ``main_script`` if a ``pages`` directory exists; else []."""
    pd = pages_dir_next_to(main_script)
    return list_page_entries(pd)


__all__ = ["PageEntry", "discover_pages", "list_page_entries", "pages_dir_next_to"]
