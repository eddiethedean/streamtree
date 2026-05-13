"""Tests for ``streamtree.helpers.tree_target``."""

from __future__ import annotations

from pathlib import Path

import pytest

from streamtree.core.element import Element
from streamtree.elements import Page
from streamtree.helpers.tree_target import load_element_from_target


def test_load_element_from_callable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pkg = tmp_path / "stt_pkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "mod.py").write_text(
        "from streamtree.elements import Page, Text\n"
        "def build():\n"
        "    return Page(Text('hi'), key='p')\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    root = load_element_from_target("stt_pkg.mod:build")
    assert isinstance(root, Element)


def test_load_element_from_instance(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pkg = tmp_path / "stt_pkg2"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "root.py").write_text(
        "from streamtree.elements import Page, Text\nROOT = Page(Text('x'))\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    root = load_element_from_target("stt_pkg2.root:ROOT")
    assert isinstance(root, Page)


def test_load_element_bad_spec() -> None:
    with pytest.raises(ValueError, match="module:attr"):
        load_element_from_target("no-colon")


def test_load_element_blank_names() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        load_element_from_target(" : ")


def test_load_element_missing_attr(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pkg = tmp_path / "stt_pkg3"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "x.py").write_text("a = 1\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(ValueError, match="has no attribute"):
        load_element_from_target("stt_pkg3.x:missing")


def test_load_element_not_element(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pkg = tmp_path / "stt_pkg4"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "bad.py").write_text("def oops():\n    return 3\n", encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(TypeError, match="not an Element"):
        load_element_from_target("stt_pkg4.bad:oops")


def test_load_element_module_not_found() -> None:
    with pytest.raises(ValueError, match="Could not import module"):
        load_element_from_target("definitely_missing_streamtree_mod_xyz:fn")
