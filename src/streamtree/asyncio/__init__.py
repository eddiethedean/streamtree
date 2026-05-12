"""Session-scoped background work with poll-friendly status (stdlib threads).

``TaskHandle`` reads and the worker thread both touch the same ``dict`` stored in
``st.session_state``. Streamlit does not document thread-safe ``session_state``
access from background threads; StreamTree uses a per-task :class:`threading.Lock`
around shared dict fields so status, result, and error updates stay consistent
when polled from the main rerun thread.

Treat handles as **rerun-polled**: do not assume every intermediate status is
visible between bytecode steps; wait for the next Streamlit rerun to observe
updates after work completes or fails.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

import streamlit as st

T = TypeVar("T")
_LockType = type(threading.Lock())


def _task_session_key(user_key: str) -> str:
    if not user_key.strip():
        raise ValueError("async task key must be a non-empty string")
    return f"streamtree.asyncio.task.{user_key.strip()}"


def _with_box_lock(box: dict[str, Any], fn: Callable[[], T]) -> T:
    lk = box.get("_lock")
    if isinstance(lk, _LockType):
        with lk:
            return fn()
    return fn()


@dataclass(frozen=True)
class TaskHandle(Generic[T]):
    """Handle to a background task stored in ``st.session_state`` (poll ``status`` / ``result``)."""

    _session_key: str

    def status(self) -> str:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return "missing"

        def read() -> str:
            return str(box.get("status", "missing"))

        return _with_box_lock(box, read)

    def result(self) -> T | None:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return None

        def read() -> T | None:
            return box.get("result")  # type: ignore[return-value]

        return _with_box_lock(box, read)

    def error(self) -> str | None:
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return None

        def read() -> str | None:
            err = box.get("error")
            return None if err is None else str(err)

        return _with_box_lock(box, read)

    def cancel(self) -> None:
        """Request cancellation before work starts; running threads are not force-killed."""
        box = st.session_state.get(self._session_key)
        if not isinstance(box, dict):
            return

        def write() -> None:
            if box.get("status") == "pending":
                box["status"] = "cancelled"

        _with_box_lock(box, write)


def submit(fn: Callable[..., T], /, *args: Any, key: str, **kwargs: Any) -> TaskHandle[T]:
    """Run ``fn`` in a daemon thread; store progress in ``st.session_state`` under a stable key.

    The first ``submit`` for ``key`` starts the thread; later reruns return the same logical handle
    without starting duplicate work.

    Poll ``TaskHandle`` from the main Streamlit thread on reruns. A lock serializes updates to the
    internal status dict with your reads; ``fn`` itself still runs outside that lock so long work
    does not block status queries.
    """
    sk = _task_session_key(key)
    existing = st.session_state.get(sk)
    if isinstance(existing, dict) and existing.get("_submitted"):
        return TaskHandle(_session_key=sk)

    box: dict[str, Any] = {
        "status": "pending",
        "result": None,
        "error": None,
        "_submitted": True,
        "_lock": threading.Lock(),
    }
    st.session_state[sk] = box

    def run() -> None:
        def mark_running_or_abort() -> bool:
            """Return True if cancelled before start."""
            if box.get("status") == "cancelled":
                return True
            box["status"] = "running"
            return False

        if _with_box_lock(box, mark_running_or_abort):
            return
        try:
            result = fn(*args, **kwargs)
        except BaseException as exc:
            err = repr(exc)

            def mark_error() -> None:
                box["error"] = err
                box["status"] = "error"

            _with_box_lock(box, mark_error)
            return

        def mark_done() -> None:
            box["result"] = result
            box["status"] = "done"

        _with_box_lock(box, mark_done)

    threading.Thread(target=run, daemon=True, name=f"streamtree-async-{key}").start()
    return TaskHandle(_session_key=sk)


__all__ = ["TaskHandle", "submit"]
