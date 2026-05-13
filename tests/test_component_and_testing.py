"""Exercise ``streamtree.render`` and ``render_to_tree`` edge cases."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from unittest.mock import patch

import pytest

from streamtree import render
from streamtree.core.component import component
from streamtree.core.context import render_context
from streamtree.core.element import ComponentCall, Element
from streamtree.elements import Page, Text
from streamtree.testing import render_to_tree


@dataclass(frozen=True)
class Unknown(Element):
    """Not handled by ``_node``."""

    pass


def test_render_invokes_streamlit_renderer() -> None:
    seen: list[object] = []

    def capture(root: object, **kwargs: object) -> None:
        seen.append(root)

    cmod = importlib.import_module("streamtree.core.component")
    with patch.object(cmod, "_render_streamlit_tree", capture):
        render(Page(Text("z"), key="root"))

    assert len(seen) == 1
    assert isinstance(seen[0], Page)


def test_render_to_tree_expand_component() -> None:
    @component
    def Inner() -> Element:
        return Text("expanded")

    with render_context("ctx"):
        tree = render_to_tree(Page(Inner()), expand_components=True)
    assert tree["kind"] == "Page"
    assert tree["children"][0]["kind"] == "Text"
    assert tree["children"][0]["body"] == "expanded"


def test_render_to_tree_expand_component_none_raises() -> None:
    @component
    def Bad() -> Element | None:
        return None  # type: ignore[return-value]

    with render_context("ctx"), pytest.raises(TypeError, match="returned None"):
        render_to_tree(Page(Bad()), expand_components=True)


def test_render_to_tree_expand_component_non_element_raises() -> None:
    @component
    def Bad2() -> Element:
        return "nope"  # type: ignore[return-value]

    with render_context("ctx"), pytest.raises(TypeError, match="returned"):
        render_to_tree(Page(Bad2()), expand_components=True)


def test_render_to_tree_unknown_element_raises() -> None:
    with pytest.raises(TypeError, match="Unsupported"):
        render_to_tree(Unknown())  # type: ignore[arg-type]


def test_safe_repr_nested() -> None:
    @component
    def WithArgs(x: object) -> Element:
        return Text("t")

    tree = render_to_tree(
        ComponentCall(
            fn=WithArgs,
            args=(Text("nested"),),
            kwargs={"k": {"inner": Text("x")}},
        )
    )
    assert tree["kind"] == "ComponentCall"
    assert isinstance(tree["args"], list)
    assert isinstance(tree["kwargs"]["k"], dict)


def test_safe_repr_primitives_in_component_call() -> None:
    def f() -> Element:
        return Text("a")

    tree = render_to_tree(
        ComponentCall(
            fn=f,
            args=(42, "s", 1.5, True, None),
            kwargs={"z": 0},
        )
    )
    assert tree["args"] == [42, "s", 1.5, True, None]
    assert tree["kwargs"] == {"z": 0}


def test_safe_repr_fallback_repr() -> None:
    tree = render_to_tree(
        ComponentCall(
            fn=lambda: Text("a"),
            args=(object(),),
            kwargs={},
        )
    )
    assert "args" in tree
