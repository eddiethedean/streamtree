"""Tests for streamtree.helpers.pages."""

from __future__ import annotations

from pathlib import Path

from streamtree.helpers.pages import (
    PageEntry,
    discover_pages,
    list_page_entries,
    pages_dir_next_to,
)


def test_pages_dir_next_to(tmp_path: Path) -> None:
    main = tmp_path / "app" / "main.py"
    main.parent.mkdir(parents=True)
    main.write_text("#", encoding="utf-8")
    assert pages_dir_next_to(main) == main.parent / "pages"


def test_list_page_entries_empty_dir(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    assert list_page_entries(pages) == []


def test_list_page_entries_missing_returns_empty(tmp_path: Path) -> None:
    assert list_page_entries(tmp_path / "nope") == []


def test_list_page_entries_orders_and_labels(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "10_Zebra.py").write_text("#", encoding="utf-8")
    (pages / "2_Alpha_Beta.py").write_text("#", encoding="utf-8")
    (pages / "Plain.py").write_text("#", encoding="utf-8")
    (pages / "_skip.py").write_text("#", encoding="utf-8")
    (pages / "__init__.py").write_text("#", encoding="utf-8")
    (pages / "notes.txt").write_text("x", encoding="utf-8")

    got = list_page_entries(pages)
    labels = [e.label for e in got]
    assert labels == ["Alpha Beta", "Zebra", "Plain"]
    assert got[0].sort_key == (2, "2_alpha_beta")
    assert got[0].page == "pages/2_Alpha_Beta.py"
    assert got[1].sort_key == (10, "10_zebra")
    assert got[2].sort_key == (1_000_000, "plain")


def test_discover_pages(tmp_path: Path) -> None:
    app = tmp_path / "run.py"
    app.write_text("#", encoding="utf-8")
    pages = app.parent / "pages"
    pages.mkdir()
    (pages / "1_Home.py").write_text("#", encoding="utf-8")

    entries = discover_pages(app)
    assert len(entries) == 1
    assert isinstance(entries[0], PageEntry)
    assert entries[0].label == "Home"


def test_page_entry_is_frozen() -> None:
    p = Path("/tmp/x/pages/1_A.py")
    e = PageEntry(
        path=p,
        stem="1_A",
        sort_key=(1, "1_a"),
        label="A",
        page="pages/1_A.py",
    )
    assert e.label == "A"
