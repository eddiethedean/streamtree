"""Session-scoped background work with poll-friendly status (stdlib threads)."""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import streamlit as st

T = TypeVar("T")


def _task_session_key(user_key: str) -> str:
    if not user_key.strip():
        raise ValueError("async task key must be a non-empty string")
    return f"streamtree.asyncio.task.{user_key.strip()}"


@dataclass(frozen=True)
class TaskHandle(Generic[T]):
    """Handle to a background task stored in ``st.session_state`` (poll ``status`` / ``result``)."""

    _session_key: str

    def status(self) -> str:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return "missing"
        return str(box.get("status", "missing"))

    def result(self) -> T | None:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return None
        return box.get("result")  # type: ignore[return-value]

    def error(self) -> str | None:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return None
        err = box.get("error")
        return None if err is None else str(err)

    def cancel(self) -> None:
        """Request cancellation before work starts; running threads are not force-killed."""
        box = st.session_state.get(self._session_key)
        if isinstance(box, dict) and box.get("status") == "pending":
            box["status"] = "cancelled"


def submit(fn: Callable[..., T], /, *args: Any, key: str, **kwargs: Any) -> TaskHandle[T]:
    """Run ``fn`` in a daemon thread; store progress in ``st.session_state`` under a stable key.

    The first ``submit`` for ``key`` starts the thread; later reruns return the same logical handle
    without starting duplicate work.
    """
    sk = _task_session_key(key)
    box = st.session_state.get(sk)
    if isinstance(box, dict) and box.get("_submitted"):
        return TaskHandle(_session_key=sk)

    box: dict[str, Any] = {"status": "pending", "result": None, "error": None, "_submitted": True}
    st.session_state[sk] = box

    def run() -> None:
        if box.get("status") == "cancelled":  # pragma: no cover
            return
        try:
            box["status"] = "running"
            box["result"] = fn(*args, **kwargs)
            box["status"] = "done"
        except BaseException as exc:
            box["error"] = repr(exc)
            box["status"] = "error"

    threading.Thread(target=run, daemon=True, name=f"streamtree-async-{key}").start()
    return TaskHandle(_session_key=sk)


__all__ = ["TaskHandle", "submit"]
