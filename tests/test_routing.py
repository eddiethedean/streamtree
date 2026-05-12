"""Tests for streamtree.routing."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from streamtree import routing as routing_mod
from streamtree.routing import set_route, sync_route

_SK_ROUTE = "streamtree.routing.active.route"


def test_sync_route_from_query() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": "about"})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "about"
    assert st.session_state[_SK_ROUTE] == "about"


def test_sync_route_strips_query_value() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": "  about  "})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "about"
    assert st.session_state[_SK_ROUTE] == "about"


def test_sync_route_default_writes_query() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"
    assert st.session_state[_SK_ROUTE] == "home"
    assert qp["route"] == "home"


def test_set_route_strips_name() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        set_route("  settings  ", param="route")
    assert st.session_state[_SK_ROUTE] == "settings"
    assert qp["route"] == "settings"


def test_sync_route_from_query_list_first() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": ["listy", "ignored"]})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "listy"


def test_set_route() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        set_route("settings", param="route")
    assert st.session_state[_SK_ROUTE] == "settings"
    assert qp["route"] == "settings"


def test_sync_route_uses_session_when_query_empty() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(
        session_state={_SK_ROUTE: "saved"},
        query_params=qp,
    )
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "saved"
    assert qp["route"] == "saved"


def test_sync_route_ignores_whitespace_only_query() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": "   "})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"
    assert st.session_state[_SK_ROUTE] == "home"


def test_sync_route_ignores_empty_query_list() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": []})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"


def test_sync_route_normalizes_whitespace_session_to_default() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={_SK_ROUTE: "  "}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"
    assert st.session_state[_SK_ROUTE] == "home"


def test_sync_route_strips_default_and_param() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_route("  home  ", param="  route  ") == "home"
    assert qp["route"] == "home"


def test_sync_route_none_query_value_ignored() -> None:
    st = SimpleNamespace(session_state={}, query_params={"route": None})
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"
    assert st.session_state[_SK_ROUTE] == "home"


def test_two_params_use_independent_session_keys() -> None:
    qp: dict[str, str] = {"route": "alpha", "tab": "settings"}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "alpha"
        assert sync_route("overview", param="tab") == "settings"
    assert st.session_state["streamtree.routing.active.route"] == "alpha"
    assert st.session_state["streamtree.routing.active.tab"] == "settings"


def test_first_returns_none_for_none() -> None:
    assert routing_mod._first(None) is None


@pytest.mark.parametrize(
    ("fn", "kwargs"),
    [
        (sync_route, {"default": "", "param": "route"}),
        (sync_route, {"default": "   ", "param": "route"}),
        (sync_route, {"default": "home", "param": ""}),
        (sync_route, {"default": "home", "param": "  "}),
        (set_route, {"name": "", "param": "route"}),
        (set_route, {"name": "  ", "param": "route"}),
        (set_route, {"name": "home", "param": ""}),
        (set_route, {"name": "home", "param": "  "}),
    ],
)
def test_routing_rejects_blank_strings(
    fn: object,
    kwargs: dict[str, str],
) -> None:
    st = SimpleNamespace(session_state={}, query_params={})
    with patch("streamtree.routing.st", st), pytest.raises(ValueError):
        fn(**kwargs)  # type: ignore[misc]
