"""Runtime helpers for StreamTree-owned ``st.session_state`` keys (dev / tests)."""

from __future__ import annotations

from typing import Any

import streamlit as st


def _classify_streamtree_key(key: str) -> str:
    if key.startswith("streamtree.asyncio.task."):
        return "async_task"
    if key.startswith("streamtree.state."):
        return "state_explicit"
    if key.startswith("streamtree.memo_subtree."):
        return "memo_subtree"
    if key.startswith("streamtree.memo."):
        return "memo"
    if key.startswith("streamtree.cache."):
        return "cache"
    if key.startswith("streamtree.routing.active."):
        return "routing"
    if key.startswith("streamtree.query.value."):
        return "query"
    if key.startswith("streamtree.widget."):
        return "widget"
    if key.startswith("streamtree.app."):
        return "app"
    return "other"


def iter_streamtree_session_keys() -> list[str]:
    """Return sorted ``st.session_state`` keys managed by StreamTree conventions."""
    return sorted(
        k for k in st.session_state.keys() if isinstance(k, str) and k.startswith("streamtree.")
    )


def summarize_streamtree_session_state() -> list[dict[str, Any]]:
    """Summarize StreamTree session slots (key, category, value type name).

    Values are not serialized in depth (widgets and task dicts can be large); this is
    for debugging and logging only.
    """
    rows: list[dict[str, Any]] = []
    for key in iter_streamtree_session_keys():
        val = st.session_state.get(key)
        rows.append(
            {
                "key": key,
                "category": _classify_streamtree_key(key),
                "value_type": type(val).__name__,
            }
        )
    return rows


__all__ = ["iter_streamtree_session_keys", "summarize_streamtree_session_state"]
