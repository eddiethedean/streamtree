"""Application shell: page config and optional sidebar + main layout."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from streamtree.core.element import Element
from streamtree.elements.layout import Page, Sidebar

_SESSION_PAGE_CONFIG = "streamtree.app.page_config_applied"


@dataclass(frozen=True)
class App:
    """Root shell: ``st.set_page_config`` (once per session) plus main body and optional sidebar.

    Compose the main area with ``Page``, ``Routes``, etc. When ``sidebar`` is set,
    it is rendered in ``st.sidebar`` before the main ``body`` (via ``Page`` ordering).
    """

    body: Element
    sidebar: Element | None = None
    page_title: str = "Streamtree"
    page_icon: str | None = None
    layout: Literal["centered", "wide"] = "centered"


def apply_page_config(app: App) -> None:
    """Call ``st.set_page_config`` at most once per session (Streamlit allows one early call)."""
    if st.session_state.get(_SESSION_PAGE_CONFIG):
        return
    if app.page_icon is not None:
        st.set_page_config(
            page_title=app.page_title,
            layout=app.layout,
            page_icon=app.page_icon,
        )
    else:
        st.set_page_config(page_title=app.page_title, layout=app.layout)
    st.session_state[_SESSION_PAGE_CONFIG] = True


def app_root_element(app: App) -> Element:
    """Map ``App`` to a single :class:`Element` tree for the Streamlit renderer."""
    if app.sidebar is not None:
        return Page(Sidebar(app.sidebar), app.body)
    return app.body


__all__ = ["App", "apply_page_config", "app_root_element", "_SESSION_PAGE_CONFIG"]
