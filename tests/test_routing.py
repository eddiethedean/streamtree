"""Tests for streamtree.routing."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

from streamtree import routing as routing_mod
from streamtree.routing import set_query_value, set_route, sync_query_value, sync_route

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


def test_sync_route_final_compare_normalizes_list_query_value() -> None:
    """Avoid rewriting query when ``get`` returns a list that normalizes to the active name."""

    class _TwoPhaseGet:
        __slots__ = ("_n", "writes", "_store")

        def __init__(self) -> None:
            self._n = 0
            self.writes = 0
            self._store: dict[str, object] = {}

        def get(self, param: str) -> object | None:
            self._n += 1
            if self._n == 1:
                return None
            return self._store.get(param, ["home"])

        def __setitem__(self, key: str, value: object) -> None:
            self.writes += 1
            self._store[key] = value

    qp = _TwoPhaseGet()
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_route("home", param="route") == "home"
    assert qp.writes == 0


def test_first_returns_none_for_none() -> None:
    assert routing_mod._first(None) is None


_SK_Q = "streamtree.query.value.q"


def test_sync_query_value_reads_url() -> None:
    st = SimpleNamespace(session_state={}, query_params={"q": "hello"})
    with patch("streamtree.routing.st", st):
        assert sync_query_value("", param="q") == "hello"
    assert st.session_state[_SK_Q] == "hello"


def test_sync_query_value_default_writes_url() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_query_value("all", param="q") == "all"
    assert st.session_state[_SK_Q] == "all"
    assert qp["q"] == "all"


def test_sync_query_value_empty_string_from_url() -> None:
    st = SimpleNamespace(session_state={}, query_params={"q": ""})
    with patch("streamtree.routing.st", st):
        assert sync_query_value("fallback", param="q") == ""
    assert st.session_state[_SK_Q] == ""


def test_sync_query_value_uses_session_when_url_missing() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={_SK_Q: "saved"}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_query_value("def", param="q") == "saved"
    assert qp["q"] == "saved"


def test_set_query_value_coerces_and_sets_both() -> None:
    qp: dict[str, str] = {}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        set_query_value(42, param="n")
    assert qp["n"] == "42"
    assert st.session_state["streamtree.query.value.n"] == "42"


def test_sync_query_value_empty_query_list() -> None:
    st = SimpleNamespace(session_state={}, query_params={"q": []})
    with patch("streamtree.routing.st", st):
        assert sync_query_value("d", param="q") == ""
    assert st.session_state["streamtree.query.value.q"] == ""


def test_sync_query_value_query_as_list_strips() -> None:
    st = SimpleNamespace(session_state={}, query_params={"q": ["  hi  "]})
    with patch("streamtree.routing.st", st):
        assert sync_query_value("", param="q") == "hi"
    assert st.session_state["streamtree.query.value.q"] == "hi"


def test_two_query_params_independent() -> None:
    qp = {"a": "1", "b": "2"}
    st = SimpleNamespace(session_state={}, query_params=qp)
    with patch("streamtree.routing.st", st):
        assert sync_query_value("", param="a") == "1"
        assert sync_query_value("", param="b") == "2"


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
        (sync_query_value, {"default": "x", "param": ""}),
        (sync_query_value, {"default": "x", "param": "  "}),
        (set_query_value, {"value": "x", "param": ""}),
        (set_query_value, {"value": "x", "param": "  "}),
    ],
)
def test_routing_rejects_blank_strings(
    fn: object,
    kwargs: dict[str, str],
) -> None:
    st = SimpleNamespace(session_state={}, query_params={})
    with patch("streamtree.routing.st", st), pytest.raises(ValueError):
        fn(**kwargs)  # type: ignore[misc]
