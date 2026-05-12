"""Tests for streamtree.core.element."""

from __future__ import annotations

import pytest

from streamtree.core.element import (
    ComponentCall,
    Element,
    Fragment,
    fragment,
    normalize_children,
)


def test_normalize_children_empty() -> None:
    assert normalize_children(()) == ()


def test_normalize_children_flat() -> None:
    a = Element(key="a")
    b = Element(key="b")
    assert normalize_children((a, b)) == (a, b)


def test_normalize_children_skips_none() -> None:
    a = Element()
    assert normalize_children((a, None)) == (a,)


def test_normalize_children_nested_list() -> None:
    a = Element(key="a")
    b = Element(key="b")
    assert normalize_children(([a, b],)) == (a, b)


def test_normalize_children_nested_tuple() -> None:
    a = Element(key="a")
    assert normalize_children(((a,),)) == (a,)


def test_normalize_children_nested_empty_sequence() -> None:
    assert normalize_children(([],)) == ()


def test_normalize_children_invalid_raises() -> None:
    with pytest.raises(TypeError, match="Invalid child type"):
        normalize_children((42,))  # type: ignore[arg-type]


def test_fragment_factory() -> None:
    a = Element()
    b = Element()
    f = fragment(a, b, key="fk")
    assert isinstance(f, Fragment)
    assert f.key == "fk"
    assert len(f.children) == 2


def test_component_call_construct() -> None:
    def inner() -> Element:
        return Element(key="x")

    c = ComponentCall(fn=inner, args=(), kwargs={}, key="ck")
    assert c.fn is inner
    assert c.key == "ck"
