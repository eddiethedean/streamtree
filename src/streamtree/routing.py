"""URL query param ↔ session helpers (routes, filters, and arbitrary string params)."""

from __future__ import annotations

import streamlit as st

_DEFAULT_PARAM = "route"


def _active_session_key(param: str) -> str:
    """Session slot for the active route name, namespaced by query param."""
    return f"streamtree.routing.active.{param}"


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


def _query_value_session_key(param: str) -> str:
    """Session slot for a generic query param value (filters, sort keys, etc.)."""
    return f"streamtree.query.value.{param}"


def _coerce_query_string(raw: object) -> str:
    """First query segment as a stripped string (may be empty)."""
    if isinstance(raw, (list, tuple)):
        if not raw:
            return ""
        return str(raw[0]).strip()
    return str(raw).strip()


def sync_query_value(default: str, *, param: str) -> str:
    """Keep ``st.session_state`` and ``st.query_params[param]`` aligned for an arbitrary string.

    Unlike :func:`sync_route`, ``default`` may be empty, and a present (possibly empty)
    query value always wins: if ``param`` appears in the query string, its first segment
    (after strip) is stored in session and returned.

    Session key: ``streamtree.query.value.<param>``.
    """
    param = _validate_param(param)
    sk = _query_value_session_key(param)

    if param in st.query_params:
        raw = st.query_params[param]
        val = _coerce_query_string(raw)
        st.session_state[sk] = val
        return val

    if sk in st.session_state:
        val = str(st.session_state[sk])
    else:
        val = default
        st.session_state[sk] = val

    st.query_params[param] = val
    return val


def set_query_value(value: str, *, param: str) -> None:
    """Set a query param and mirrored session value (coerced to ``str``)."""
    param = _validate_param(param)
    text = str(value)
    st.session_state[_query_value_session_key(param)] = text
    st.query_params[param] = text


def sync_route(default: str, *, param: str = _DEFAULT_PARAM) -> str:
    """Keep ``st.session_state`` and ``st.query_params[param]`` aligned.

    Session uses one key per ``param``: ``streamtree.routing.active.<param>`` (validated name).

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

    sk = _active_session_key(param)
    raw = st.query_params.get(param)
    if raw is not None:
        name = _first(raw)
        if name:
            st.session_state[sk] = name
            return name
    if sk in st.session_state:
        raw_sess = st.session_state[sk]
        name = str(raw_sess).strip() if raw_sess is not None else ""
        if not name:
            name = default
            st.session_state[sk] = name
    else:
        name = default
        st.session_state[sk] = name
    current = _first(st.query_params.get(param))
    if current != name:
        st.query_params[param] = name
    return name


def set_route(name: str, *, param: str = _DEFAULT_PARAM) -> None:
    """Switch route programmatically (updates session + query param)."""
    param = _validate_param(param)
    if not isinstance(name, str) or not name.strip():
        raise ValueError("route name must be a non-empty string")
    name = name.strip()
    st.session_state[_active_session_key(param)] = name
    st.query_params[param] = name


__all__ = ["set_query_value", "set_route", "sync_query_value", "sync_route"]
