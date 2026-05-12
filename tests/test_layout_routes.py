"""Layout edge cases for 0.2.0 elements."""

from __future__ import annotations

import pytest

from streamtree.elements import Routes
from streamtree.elements.widgets import Text


def test_routes_requires_at_least_one_route() -> None:
    with pytest.raises(ValueError, match="at least one"):
        Routes(routes=())


def test_routes_rejects_blank_query_param() -> None:
    with pytest.raises(ValueError, match="query_param"):
        Routes(routes=(("a", Text("A")),), query_param="  ")


def test_routes_rejects_blank_default() -> None:
    with pytest.raises(ValueError, match="default"):
        Routes(routes=(("a", Text("A")),), default="  ")


def test_routes_normalizes_query_param_and_default() -> None:
    r = Routes(routes=(("home", Text("H")),), default="  home  ", query_param="  page  ")
    assert r.default == "home"
    assert r.query_param == "page"


def test_routes_rejects_duplicate_route_names() -> None:
    with pytest.raises(ValueError, match="unique"):
        Routes(routes=(("home", Text("A")), ("home", Text("B"))), default="home")
