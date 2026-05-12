"""Tests for streamtree.app_context."""

from __future__ import annotations

import pytest

from streamtree.app_context import current_bag, lookup, provider


def test_lookup_empty() -> None:
    assert lookup("theme", "light") == "light"
    assert dict(current_bag()) == {}


def test_provider_merges_and_nests() -> None:
    with provider(theme="dark", tenant="a"):
        assert lookup("theme") == "dark"
        assert lookup("tenant") == "a"
        with provider(theme="light"):
            assert lookup("theme") == "light"
            assert lookup("tenant") == "a"
        assert lookup("theme") == "dark"
    assert lookup("theme", "x") == "x"


def test_current_bag_snapshot() -> None:
    with provider(x=1):
        assert current_bag()["x"] == 1


def test_current_bag_returns_shallow_copy() -> None:
    with provider(x=1):
        snap = current_bag()
        assert isinstance(snap, dict)
        snap["x"] = 99
        assert lookup("x") == 1


def test_lookup_strips_key() -> None:
    with provider(theme="dark"):
        assert lookup("  theme  ") == "dark"


def test_provider_rejects_blank_key() -> None:
    with pytest.raises(TypeError):
        with provider(**{"": 1}):
            pass


def test_provider_rejects_whitespace_only_key() -> None:
    with pytest.raises(TypeError):
        with provider(**{"  ": 1}):
            pass


def test_lookup_rejects_blank_key() -> None:
    with pytest.raises(TypeError):
        lookup("")


def test_lookup_rejects_non_string_key() -> None:
    with pytest.raises(TypeError):
        lookup(1)  # type: ignore[arg-type]
