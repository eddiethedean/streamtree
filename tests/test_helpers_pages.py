"""Tests for streamtree.helpers.pages."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from streamtree.helpers.pages import (
    PageEntry,
    discover_pages,
    group_page_entries_by_order_prefix,
    iter_page_entries,
    list_page_entries,
    multipage_sidebar_nav,
    page_links,
    page_links_sidebar_sections,
    pages_dir_next_to,
    prefetch_page_sources,
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


def test_discover_pages_returns_empty_when_pages_dir_missing(tmp_path: Path) -> None:
    main = tmp_path / "solo.py"
    main.write_text("#", encoding="utf-8")
    assert discover_pages(main) == []


def test_pages_dir_next_to_expands_user(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fake_home = tmp_path / "h"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("USERPROFILE", str(fake_home))
    tilde_main = Path("~/app/main.py")
    expected = (fake_home / "app" / "pages").resolve()
    assert pages_dir_next_to(tilde_main) == expected


def test_list_page_entries_same_order_sorts_by_stem(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_Zebra.py").write_text("#", encoding="utf-8")
    (pages / "1_Alpha.py").write_text("#", encoding="utf-8")
    got = list_page_entries(pages)
    assert [e.stem for e in got] == ["1_Alpha", "1_Zebra"]


def test_list_page_entries_stem_only_digits_unnumbered(tmp_path: Path) -> None:
    """``123.py`` has no ``digits_`` prefix pattern; treated like an unnumbered page."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "123.py").write_text("#", encoding="utf-8")
    got = list_page_entries(pages)
    assert len(got) == 1
    assert got[0].sort_key[0] == 1_000_000
    assert got[0].label == "123"


def test_list_page_entries_stem_trailing_underscore_unnumbered(tmp_path: Path) -> None:
    """``1_`` does not match ``.+`` after the order underscore; falls back to unnumbered."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_.py").write_text("#", encoding="utf-8")
    got = list_page_entries(pages)
    assert len(got) == 1
    assert got[0].stem == "1_"
    assert got[0].sort_key[0] == 1_000_000


def test_list_page_entries_unicode_label(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    name = "2_Docs_über_uns.py"
    (pages / name).write_text("# -*- coding: utf-8 -*-", encoding="utf-8")
    got = list_page_entries(pages)
    assert len(got) == 1
    assert got[0].label == "Docs über uns"
    assert "über" in got[0].page


def test_list_page_entries_ignores_subdirectories(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    nested = pages / "nested"
    nested.mkdir()
    (nested / "Hidden.py").write_text("#", encoding="utf-8")
    (pages / "1_Top.py").write_text("#", encoding="utf-8")
    got = list_page_entries(pages)
    assert len(got) == 1
    assert got[0].stem == "1_Top"


def test_list_page_entries_numeric_padding_sorts_lexically_by_stem(tmp_path: Path) -> None:
    """Same numeric prefix: secondary sort is ``stem.lower()`` (stable, deterministic)."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_02_second.py").write_text("#", encoding="utf-8")
    (pages / "1_01_first.py").write_text("#", encoding="utf-8")
    got = list_page_entries(pages)
    assert [e.stem for e in got] == ["1_01_first", "1_02_second"]


def test_list_page_entries_internal_symlink_keeps_sidebar_name(tmp_path: Path) -> None:
    """Symlink to another file in the same ``pages/`` dir is listed; ``stem`` is the link name."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "0_Base.py").write_text("#", encoding="utf-8")
    link = pages / "3_Linked.py"
    try:
        link.symlink_to(Path("0_Base.py"))
    except OSError:
        pytest.skip("symlinks not supported")
    got = list_page_entries(pages)
    by_stem = {e.stem: e for e in got}
    assert set(by_stem) == {"0_Base", "3_Linked"}
    assert by_stem["3_Linked"].label == "Linked"


def test_list_page_entries_skips_symlink_outside_project_root(tmp_path: Path) -> None:
    """A ``pages/*.py`` symlink whose target resolves outside the app dir is skipped."""
    app = tmp_path / "app"
    pages = app / "pages"
    pages.mkdir(parents=True)
    outside = tmp_path / "outside_target.py"
    outside.write_text("# ext\n", encoding="utf-8")
    link = pages / "9_Outside.py"
    try:
        link.symlink_to(outside.resolve())
    except OSError:
        pytest.skip("symlinks not supported")
    (pages / "1_Valid.py").write_text("# ok\n", encoding="utf-8")
    got = list_page_entries(pages)
    assert [e.stem for e in got] == ["1_Valid"]


def test_list_page_entries_accepts_str_path(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_One.py").write_text("#", encoding="utf-8")
    got = list_page_entries(str(pages))
    assert len(got) == 1
    assert got[0].label == "One"


def test_discover_pages_accepts_str_path(tmp_path: Path) -> None:
    main = tmp_path / "app.py"
    main.write_text("#", encoding="utf-8")
    pages = main.parent / "pages"
    pages.mkdir()
    (pages / "1_X.py").write_text("#", encoding="utf-8")
    entries = discover_pages(str(main))
    assert len(entries) == 1
    assert entries[0].label == "X"


def test_page_links_builds_page_link_widgets(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_Hello.py").write_text("#", encoding="utf-8")
    entries = list_page_entries(pages)
    links = page_links(entries, icon="🌐", disabled=False)
    assert len(links) == 1
    assert links[0].label == "Hello"
    assert links[0].page == "pages/1_Hello.py"
    assert links[0].icon == "🌐"


def test_iter_page_entries_matches_list_page_entries(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "2_B.py").write_text("#", encoding="utf-8")
    (pages / "1_A.py").write_text("#", encoding="utf-8")
    assert list(iter_page_entries(pages)) == list_page_entries(pages)


def test_prefetch_page_sources_compile_ok(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_Ok.py").write_text("x = 1\n", encoding="utf-8")
    entries = list_page_entries(pages)
    out = prefetch_page_sources(entries)
    assert len(out) == 1
    assert out[0][1] is None


def test_prefetch_page_sources_syntax_error(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_Bad.py").write_text("def broken(\n", encoding="utf-8")
    entries = list_page_entries(pages)
    out = prefetch_page_sources(entries)
    assert out[0][1] is not None


def test_prefetch_page_sources_no_compile(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_Bad.py").write_text("(((", encoding="utf-8")
    entries = list_page_entries(pages)
    out = prefetch_page_sources(entries, compile_check=False)
    assert out[0][1] is None


def test_prefetch_page_sources_oserror(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_X.py").write_text("x = 1\n", encoding="utf-8")
    entries = list_page_entries(pages)
    orig = Path.read_text

    def boom(self: Path, *a: object, **kw: object) -> str:
        if self.name == "1_X.py":
            raise OSError("simulated read failure")
        return orig(self, *a, **kw)

    with patch.object(Path, "read_text", boom):
        out = prefetch_page_sources(entries)
    assert len(out) == 1
    assert "simulated read failure" in (out[0][1] or "")


def test_group_page_entries_by_order_prefix(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_A.py").write_text("#", encoding="utf-8")
    (pages / "1_B.py").write_text("#", encoding="utf-8")
    (pages / "2_C.py").write_text("#", encoding="utf-8")
    (pages / "Plain.py").write_text("#", encoding="utf-8")
    entries = list_page_entries(pages)
    groups = group_page_entries_by_order_prefix(entries)
    keys = [g[0] for g in groups]
    assert "1" in keys and "2" in keys
    assert None in keys
    by_key = {k: v for k, v in groups}
    assert len(by_key["1"]) == 2
    assert len(by_key["2"]) == 1
    assert len(by_key[None]) == 1


def test_page_links_sidebar_sections_has_subheaders(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_One.py").write_text("#", encoding="utf-8")
    (pages / "Zed.py").write_text("#", encoding="utf-8")
    entries = list_page_entries(pages)
    flat = page_links_sidebar_sections(entries)
    from streamtree.elements.widgets import PageLink, Subheader

    assert any(isinstance(x, Subheader) for x in flat)
    assert sum(1 for x in flat if isinstance(x, PageLink)) == 2


def test_multipage_sidebar_nav_empty(tmp_path: Path) -> None:
    main = tmp_path / "app.py"
    main.write_text("#", encoding="utf-8")
    nav = multipage_sidebar_nav(main)
    assert len(nav.children) == 0


def test_multipage_sidebar_nav_flat_without_sections(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_A.py").write_text("#", encoding="utf-8")
    main = tmp_path / "app.py"
    main.write_text("#", encoding="utf-8")
    nav = multipage_sidebar_nav(main, section_numbered=False)
    assert len(nav.children) == 1
    from streamtree.elements.widgets import PageLink

    assert isinstance(nav.children[0], PageLink)


def test_multipage_sidebar_nav_grouped_default(tmp_path: Path) -> None:
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "1_A.py").write_text("#", encoding="utf-8")
    main = tmp_path / "app.py"
    main.write_text("#", encoding="utf-8")
    nav = multipage_sidebar_nav(main)
    from streamtree.elements.widgets import Subheader

    assert any(isinstance(c, Subheader) for c in nav.children)
