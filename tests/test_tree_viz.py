"""Tests for ``streamtree.testing.viz`` formatters."""

from __future__ import annotations

from streamtree.testing.viz import format_tree_text, tree_dict_to_mermaid


def test_format_tree_text_non_dict_node() -> None:
    assert format_tree_text(42) == ""


def test_format_tree_text_componentcall_name() -> None:
    tree = {"kind": "ComponentCall", "key": "k", "name": "Demo", "args": [], "kwargs": {}}
    out = format_tree_text(tree)
    assert "Demo" in out


def test_tree_dict_to_mermaid_non_dict_in_list() -> None:
    m = tree_dict_to_mermaid([1, {"kind": "Text", "key": None, "body": "z"}])
    assert "flowchart TD" in m


def test_format_tree_text_label_without_name() -> None:
    tree = {"kind": "Button", "key": "b", "label": "Go", "disabled": False, "submit": False, "has_on_click": False}
    out = format_tree_text(tree)
    assert "label=" in out


def test_mermaid_error_boundary_and_split() -> None:
    eb = {
        "kind": "ErrorBoundary",
        "key": None,
        "child": {"kind": "Text", "key": None, "body": "c"},
        "fallback": {"kind": "Text", "key": None, "body": "f"},
        "has_on_error": False,
    }
    assert "ErrorBoundary" in tree_dict_to_mermaid(eb)
    split = {
        "kind": "SplitView",
        "key": None,
        "narrow_ratio": 0.2,
        "narrow": {"kind": "Text", "key": None, "body": "n"},
        "main": {"kind": "Text", "key": None, "body": "m"},
    }
    m2 = tree_dict_to_mermaid(split)
    assert "SplitView" in m2


def test_mermaid_tabs_walk() -> None:
    tree = {
        "kind": "Tabs",
        "key": None,
        "tabs": [{"title": "T", "child": {"kind": "Text", "key": None, "body": "x"}}],
    }
    assert "Tabs" in tree_dict_to_mermaid(tree)


def test_format_tree_text_list_root() -> None:
    tree = [{"kind": "Text", "key": None, "body": "a"}]
    out = format_tree_text(tree)
    assert "Text" in out


def test_tree_dict_to_mermaid_list() -> None:
    m = tree_dict_to_mermaid([{"kind": "Text", "key": None, "body": "z"}])
    assert "flowchart TD" in m


def test_format_tree_text_nested() -> None:
    tree = {
        "kind": "Page",
        "key": "p",
        "children": [
            {"kind": "Text", "key": None, "body": "hi"},
        ],
    }
    out = format_tree_text(tree)
    assert "Page" in out and "Text" in out


def test_format_tree_text_error_boundary_fallback() -> None:
    tree = {
        "kind": "ErrorBoundary",
        "key": None,
        "child": {"kind": "Text", "key": None, "body": "c"},
        "fallback": {"kind": "Text", "key": None, "body": "f"},
        "has_on_error": False,
    }
    out = format_tree_text(tree)
    assert "fallback" in out


def test_tree_dict_to_mermaid_basic() -> None:
    tree = {
        "kind": "Page",
        "key": "root",
        "children": [{"kind": "Text", "key": None, "body": "x"}],
    }
    m = tree_dict_to_mermaid(tree)
    assert m.startswith("flowchart TD")
    assert "-->" in m


def test_format_tree_text_tabs_and_split() -> None:
    tree = {
        "kind": "Tabs",
        "key": None,
        "tabs": [{"title": "A", "child": {"kind": "Text", "key": None, "body": "t"}}],
    }
    assert "tab" in format_tree_text(tree)
    split = {
        "kind": "SplitView",
        "key": None,
        "narrow_ratio": 0.2,
        "narrow": {"kind": "Text", "key": None, "body": "n"},
        "main": {"kind": "Text", "key": None, "body": "m"},
    }
    st = format_tree_text(split)
    assert "narrow" in st and "main" in st
