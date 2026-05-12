"""Tests for streamtree.app.App and render_app page config."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from streamtree.app import _SESSION_PAGE_CONFIG, App, app_root_element, apply_page_config
from streamtree.core.component import render_app
from streamtree.elements import Page, Sidebar, Text


def test_render_app_applies_config_and_renders_root() -> None:
    with (
        patch("streamtree.app.apply_page_config") as ap,
        patch("streamtree.app.app_root_element", return_value=Text("root")) as ar,
        patch("streamtree.core.component._render_streamlit") as rr,
    ):
        render_app(App(body=Text("ignored"), page_title="T"))
    ap.assert_called_once()
    ar.assert_called_once()
    rr.assert_called_once()


def test_render_app_rejects_non_app() -> None:
    with pytest.raises(TypeError):
        render_app(Text("nope"))  # type: ignore[arg-type]


def test_app_root_body_only() -> None:
    body = Text("main")
    app = App(body=body)
    assert app_root_element(app) is body


def test_app_root_with_sidebar() -> None:
    body = Text("main")
    side = Text("nav")
    app = App(body=body, sidebar=side)
    root = app_root_element(app)
    assert isinstance(root, Page)
    assert len(root.children) == 2
    assert isinstance(root.children[0], Sidebar)
    assert root.children[0].children == (side,)
    assert root.children[1] is body


def test_apply_page_config_without_icon() -> None:
    calls: list[tuple[str, object]] = []

    def fake_set_page_config(**kwargs: object) -> None:
        calls.append(("cfg", kwargs))

    st = SimpleNamespace(session_state={}, set_page_config=fake_set_page_config)
    app = App(body=Text("x"), page_title="NoIcon", page_icon=None)
    with patch("streamtree.app.st", st):
        apply_page_config(app)
    assert len(calls) == 1
    assert calls[0][1]["page_title"] == "NoIcon"
    assert "page_icon" not in calls[0][1]


def test_apply_page_config_sets_once() -> None:
    calls: list[str] = []

    def fake_set_page_config(**kwargs: object) -> None:
        calls.append("cfg")

    st = SimpleNamespace(
        session_state={},
        set_page_config=fake_set_page_config,
    )
    app = App(body=Text("x"), page_title="T", layout="wide", page_icon="🌲")
    with patch("streamtree.app.st", st):
        apply_page_config(app)
        apply_page_config(app)
    assert calls == ["cfg"]
    assert st.session_state[_SESSION_PAGE_CONFIG] is True


def test_apply_page_config_skips_when_flag_set() -> None:
    mock_cfg = MagicMock()
    st = SimpleNamespace(session_state={_SESSION_PAGE_CONFIG: True}, set_page_config=mock_cfg)
    app = App(body=Text("x"))
    with patch("streamtree.app.st", st):
        apply_page_config(app)
    mock_cfg.assert_not_called()
