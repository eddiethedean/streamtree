"""Tests for ``streamtree.helpers.scaffold``."""

from __future__ import annotations

from pathlib import Path

import pytest

from streamtree.helpers.scaffold import app_py_source, write_init_project


def test_app_py_source_embeds_title() -> None:
    src = app_py_source(page_title="My App")
    assert "page_title=" in src
    assert repr("My App") in src
    assert "render_app" in src


def test_app_py_source_repr_escapes_special_chars() -> None:
    src = app_py_source(page_title='Say "hi"')
    assert repr('Say "hi"') in src


def test_app_py_source_newlines_are_valid_python() -> None:
    src = app_py_source(page_title="Line1\nLine2")
    compile(src, "<app.py>", "exec")


def test_app_py_source_with_pages_compiles() -> None:
    src = app_py_source(page_title="NavApp", with_pages=True)
    compile(src, "<app.py>", "exec")
    assert "discover_pages" in src
    assert "page_links" in src
    assert "SidebarNav" in src


def test_write_init_project_creates_app(tmp_path: Path) -> None:
    out = write_init_project(tmp_path, page_title="T", with_pages=False, force=False)
    assert len(out) == 1
    assert out[0].name == "app.py"
    text = (tmp_path / "app.py").read_text(encoding="utf-8")
    assert "page_title=" in text
    assert repr("T") in text


def test_write_init_project_with_pages(tmp_path: Path) -> None:
    out = write_init_project(tmp_path, page_title="X", with_pages=True, force=False)
    assert len(out) == 2
    assert (tmp_path / "pages" / "1_About.py").is_file()
    app_txt = (tmp_path / "app.py").read_text(encoding="utf-8")
    assert "discover_pages" in app_txt
    assert "page_links" in app_txt


def test_write_init_project_refuses_overwrite(tmp_path: Path) -> None:
    write_init_project(tmp_path, page_title="A", with_pages=False, force=False)
    with pytest.raises(FileExistsError):
        write_init_project(tmp_path, page_title="B", with_pages=False, force=False)


def test_write_init_project_force_overwrites(tmp_path: Path) -> None:
    write_init_project(tmp_path, page_title="Old", with_pages=False, force=False)
    write_init_project(tmp_path, page_title="New", with_pages=False, force=True)
    assert repr("New") in (tmp_path / "app.py").read_text(encoding="utf-8")


def test_write_init_project_pages_file_exists(tmp_path: Path) -> None:
    write_init_project(tmp_path, page_title="P", with_pages=True, force=False)
    with pytest.raises(FileExistsError):
        write_init_project(tmp_path, page_title="P", with_pages=True, force=False)


def test_write_init_project_rejects_file_target(tmp_path: Path) -> None:
    f = tmp_path / "not_dir"
    f.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match="not a directory"):
        write_init_project(f, page_title="T", with_pages=False, force=False)
