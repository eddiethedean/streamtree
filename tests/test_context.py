"""Tests for streamtree.core.context."""

from __future__ import annotations

import pytest

from streamtree.core.context import current_context, push_segment, render_context


def test_render_context_yields_and_paths() -> None:
    with render_context("root") as ctx:
        assert ctx.parent is None
        assert ctx.path() == "root"
        with push_segment("child") as inner:
            assert inner.path() == "root.child"


def test_render_context_nested_preserves_parent() -> None:
    with render_context("a") as outer:
        with render_context("b") as inner:
            assert inner.parent is outer
            assert inner.path() == "a.b"


def test_current_context_outside_raises() -> None:
    with pytest.raises(RuntimeError, match="no active render context"):
        current_context()


def test_render_context_anonymous_counter() -> None:
    with render_context("root") as ctx:
        assert ctx.next_anonymous_index() == 0
        assert ctx.next_anonymous_index() == 1


def test_path_when_parent_path_empty() -> None:
    with render_context(""):
        with push_segment("z") as inner:
            assert inner.path() == "z"
