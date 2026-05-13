"""Session-scoped background work with poll-friendly status (stdlib threads).

``TaskHandle`` reads and the worker thread both touch the same ``dict`` stored in
``st.session_state``. Streamlit does not document thread-safe ``session_state``
access from background threads; StreamTree uses a per-task :class:`threading.Lock`
around shared dict fields so status, result, error, and **progress** updates stay
consistent when polled from the main rerun thread.

Workers may call :func:`set_task_progress` with the same ``key`` passed to :func:`submit`
to publish rerun-polled progress values.

Treat handles as **rerun-polled**: do not assume every intermediate status is
visible between bytecode steps; wait for the next Streamlit rerun to observe
updates after work completes or fails.
"""

from __future__ import annotations

import threading
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast

import streamlit as st

T = TypeVar("T")
_LockType = type(threading.Lock())


def _task_session_key(user_key: str) -> str:
    if not user_key.strip():
        raise ValueError("async task key must be a non-empty string")
    return f"streamtree.asyncio.task.{user_key.strip()}"


def _is_managed_task_box(box: object) -> bool:
    """True only for dicts installed by :func:`submit` (submitted flag + real lock)."""
    if not isinstance(box, dict):
        return False
    d = cast(dict[str, Any], box)
    return d.get("_submitted") is True and isinstance(d.get("_lock"), _LockType)


def _with_box_lock(box: dict[str, Any], fn: Callable[[], T]) -> T:
    lk = box.get("_lock")
    if isinstance(lk, _LockType):
        with lk:
            return fn()
    return fn()


def set_task_progress(*, key: str, value: Any) -> None:
    """Set the ``progress`` field for the task identified by ``key`` (same as :func:`submit`).

    Intended for use **inside** the worker function or helpers it calls. Updates are
    serialized with the same per-task lock as status/result/error. No-ops if there is
    no active task box at ``key`` (or the value at ``key`` is not a managed task dict).
    """
    sk = _task_session_key(key)
    raw = st.session_state.get(sk)
    if not _is_managed_task_box(raw):
        return
    box = cast(dict[str, Any], raw)

    def write() -> None:
        box["progress"] = value

    _with_box_lock(box, write)


@dataclass(frozen=True)
class TaskHandle(Generic[T]):
    """Handle to a background task stored in ``st.session_state`` (poll ``status`` / ``result``)."""

    _session_key: str

    def status(self) -> str:
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return "missing"
        box = cast(dict[str, Any], raw)

        def read() -> str:
            return str(box.get("status", "missing"))

        return _with_box_lock(box, read)

    def result(self) -> T | None:
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return None
        box = cast(dict[str, Any], raw)

        def read() -> T | None:
            return box.get("result")  # type: ignore[return-value]

        return _with_box_lock(box, read)

    def error(self) -> str | None:
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return None
        box = cast(dict[str, Any], raw)

        def read() -> str | None:
            err = box.get("error")
            return None if err is None else str(err)

        return _with_box_lock(box, read)

    def progress(self) -> Any | None:
        """Last progress value set via :func:`set_task_progress`, or ``None``."""
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return None
        box = cast(dict[str, Any], raw)

        def read() -> Any | None:
            return box.get("progress")

        return _with_box_lock(box, read)

    def cancel(self) -> None:
        """Request cancellation before work starts; running threads are not force-killed."""
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return
        box = cast(dict[str, Any], raw)

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
    if _is_managed_task_box(existing):
        return TaskHandle(_session_key=sk)
    if isinstance(existing, dict):
        # Corrupted or foreign mapping at our key: drop before installing a real task box.
        del st.session_state[sk]

    box: dict[str, Any] = {
        "status": "pending",
        "result": None,
        "error": None,
        "progress": None,
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
        except Exception as exc:
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


__all__ = ["TaskHandle", "set_task_progress", "submit"]
