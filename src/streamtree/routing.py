"""URL query param ↔ session helpers for simple multi-page Streamlit apps."""

from __future__ import annotations

import streamlit as st

_SESSION_ACTIVE = "streamtree.routing.active"
_DEFAULT_PARAM = "route"


def _validate_param(param: str) -> str:
    if not isinstance(param, str) or not param.strip():
        raise ValueError("routing param must be a non-empty string")
    return param.strip()


def _first(v: object) -> str | None:
    """First non-empty string segment from a query value, or ``None`` if absent."""
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        if not v:
            return None
        s = str(v[0]).strip()
        return s or None
    s = str(v).strip()
    return s or None


def sync_route(default: str, *, param: str = _DEFAULT_PARAM) -> str:
    """Keep ``st.session_state`` and ``st.query_params[param]`` aligned.

    If the query string sets ``param``, that wins and updates session. Otherwise
    the active route is read from session (initializing to ``default``), then
    written back to the query string when missing so URLs stay shareable.

    Empty or whitespace-only query values are ignored (treated like a missing param)
    so ``?route=`` does not overwrite session with a blank route.
    """
    param = _validate_param(param)
    if not isinstance(default, str) or not default.strip():
        raise ValueError("default must be a non-empty string")
    default = default.strip()

    raw = st.query_params.get(param)
    if raw is not None:
        name = _first(raw)
        if name:
            st.session_state[_SESSION_ACTIVE] = name
            return name
    if _SESSION_ACTIVE in st.session_state:
        raw_sess = st.session_state[_SESSION_ACTIVE]
        name = str(raw_sess).strip() if raw_sess is not None else ""
        if not name:
            name = default
            st.session_state[_SESSION_ACTIVE] = name
    else:
        name = default
        st.session_state[_SESSION_ACTIVE] = name
    if st.query_params.get(param) != name:
        st.query_params[param] = name
    return name


def set_route(name: str, *, param: str = _DEFAULT_PARAM) -> None:
    """Switch route programmatically (updates session + query param)."""
    param = _validate_param(param)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("route name must be a non-empty string")
    name = name.strip()
    st.session_state[_SESSION_ACTIVE] = name
    st.query_params[param] = name


__all__ = ["set_route", "sync_route"]
