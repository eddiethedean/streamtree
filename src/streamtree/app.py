"""Application shell: page config and optional sidebar + main layout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import streamlit as st

from streamtree.core.element import Element
from streamtree.elements.layout import Page, Sidebar

_SESSION_PAGE_CONFIG = "streamtree.app.page_config_applied"


@dataclass(frozen=True)
class App:
    """Root shell: ``st.set_page_config`` (once per session) plus main body and optional sidebar.

    Compose the main area with ``Page``, ``Routes``, etc. When ``sidebar`` is set,
    it is rendered in ``st.sidebar`` before the main ``body`` (via ``Page`` ordering).

    Page configuration (title, layout, icon, …) is applied at most **once per browser
    session** by :func:`apply_page_config`; changing ``App`` fields on later reruns
    does not re-run ``st.set_page_config`` until session state is cleared (Streamlit
    allows only one early ``set_page_config`` call per session).
    """

    body: Element
    sidebar: Element | None = None
    page_title: str = "StreamTree"
    page_icon: str | None = None
    layout: Literal["centered", "wide"] = "centered"
    initial_sidebar_state: Literal["auto", "expanded", "collapsed"] | None = None
    menu_items: dict[str, Any] | None = None


def apply_page_config(app: App) -> None:
    """Call ``st.set_page_config`` at most once per session (Streamlit allows one early call).

    After the first successful call, a flag in ``st.session_state`` prevents repeats
    for that session so reruns do not raise Streamlit API errors. To change layout or
    title mid-session, clear the relevant session state or restart the app.
    """
    if st.session_state.get(_SESSION_PAGE_CONFIG):
        return
    kwargs: dict[str, Any] = {
        "page_title": app.page_title,
        "layout": app.layout,
    }
    if app.page_icon is not None:
        kwargs["page_icon"] = app.page_icon
    if app.initial_sidebar_state is not None:
        kwargs["initial_sidebar_state"] = app.initial_sidebar_state
    if app.menu_items is not None:
        kwargs["menu_items"] = app.menu_items
    st.set_page_config(**kwargs)
    st.session_state[_SESSION_PAGE_CONFIG] = True


def app_root_element(app: App) -> Element:
    """Map ``App`` to a single :class:`Element` tree for the Streamlit renderer."""
    if app.sidebar is not None:
        return Page(Sidebar(app.sidebar), app.body)
    return app.body


__all__ = ["App", "apply_page_config", "app_root_element", "_SESSION_PAGE_CONFIG"]
