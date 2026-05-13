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

Stale runs and keys
---------------------

The first :func:`submit` for a given ``key`` owns that session slot until the task
dict is removed or replaced. Later reruns that call :func:`submit` with the **same**
``key`` return the **same** logical :class:`TaskHandle` without starting duplicate
work. To represent **new** work after a logical supersession (new user action,
new query generation, etc.), choose a **fresh** ``key`` (for example include a
monotonic id stored in ``st.session_state`` or a query token).

Cooperative cancellation
------------------------

Daemon threads cannot be force-stopped safely. :meth:`TaskHandle.cancel` on a
**pending** task marks it **cancelled** before the worker starts. On a **running**
task it sets ``cancel_requested``; the worker should poll :func:`is_task_cancel_requested`
and then call :func:`complete_cancelled` when exiting early. If the worker finishes
normally instead, **done** / **error** wins over a late cancel request (the normal
completion path clears the cancel flag).

Composition with trees
------------------------

Use :func:`submit_many` for parallel independent tasks. For declarative loading branches,
:func:`streamtree.loading.match_task` maps a :class:`TaskHandle` ``status`` to
``loading`` / ``ready`` / ``error`` element subtrees (see ``examples/async_loader_demo.py``).

After a terminal **done** / **error** / **cancelled** run, :func:`dismiss_task` removes the
session entry for a ``key`` so the next :func:`submit` can reuse that key without colliding
with stale task state. Use :func:`dismiss_tasks` to clear several terminal keys in one call
(return count of successful removals).
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Sequence
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


def is_task_cancel_requested(*, key: str) -> bool:
    """Return whether the UI thread requested cancel for a **running** task (worker polls)."""
    sk = _task_session_key(key)
    raw = st.session_state.get(sk)
    if not _is_managed_task_box(raw):
        return False
    box = cast(dict[str, Any], raw)

    def read() -> bool:
        return bool(box.get("cancel_requested"))

    return _with_box_lock(box, read)


def complete_cancelled(*, key: str) -> None:
    """Mark a **running** task as **cancelled** after the worker exits early (cooperative cancel).

    No-ops unless ``status`` is **running** and :func:`is_task_cancel_requested` would be
    true. Safe to call from the worker thread; uses the same per-task lock as other
    mutations.
    """
    sk = _task_session_key(key)
    raw = st.session_state.get(sk)
    if not _is_managed_task_box(raw):
        return
    box = cast(dict[str, Any], raw)

    def write() -> None:
        if box.get("status") == "running" and box.get("cancel_requested"):
            box["status"] = "cancelled"
            box["result"] = None
            box["error"] = None
            box["progress"] = None
            box["cancel_requested"] = False

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
        """Cancel **pending** work, or request cooperative cancel while **running**.

        Running daemon threads are not force-killed; use :func:`is_task_cancel_requested`
        and :func:`complete_cancelled` inside long workers.
        """
        raw = st.session_state.get(self._session_key)
        if not _is_managed_task_box(raw):
            return
        box = cast(dict[str, Any], raw)

        def write() -> None:
            stat = box.get("status")
            if stat == "pending":
                box["status"] = "cancelled"
            elif stat == "running":
                box["cancel_requested"] = True

        _with_box_lock(box, write)


def submit_many(jobs: Sequence[tuple[str, Callable[[], Any]]]) -> tuple[TaskHandle[Any], ...]:
    """Start several independent tasks (gather-style); each entry is ``(key, fn)``.

    Keys must be unique after stripping; raises :exc:`ValueError` on duplicates or
    blank keys. Returns a tuple of :class:`TaskHandle` in the same order as ``jobs``.
    An empty ``jobs`` sequence returns an empty tuple.
    """
    seen: set[str] = set()
    out: list[TaskHandle[Any]] = []
    for key, fn in jobs:
        if not isinstance(key, str) or not key.strip():
            raise ValueError("submit_many: each task key must be a non-empty string")
        k = key.strip()
        if k in seen:
            raise ValueError(f"submit_many: duplicate task key {k!r}")
        seen.add(k)
        out.append(submit(fn, key=k))
    return tuple(out)


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
        "cancel_requested": False,
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
                box["cancel_requested"] = False

            _with_box_lock(box, mark_error)
            return

        def mark_done() -> None:
            # Worker may have called :func:`complete_cancelled` (``cancelled``); do not overwrite.
            if box.get("status") != "running":
                return
            box["result"] = result
            box["status"] = "done"
            box["cancel_requested"] = False

        _with_box_lock(box, mark_done)

    threading.Thread(target=run, daemon=True, name=f"streamtree-async-{key}").start()
    return TaskHandle(_session_key=sk)


def dismiss_task(*, key: str) -> bool:
    """Remove a **terminal** task entry so the next :func:`submit` with the same ``key`` starts fresh.

    Returns ``True`` if session state under ``key`` was cleared. Returns ``False`` if there
    was no task, the value was not a managed task box, or status was still **pending** /
    **running** (avoids leaving a background thread writing to discarded state).

    For **running** work, prefer :meth:`TaskHandle.cancel` and cooperative shutdown; call
    ``dismiss_task`` after the handle reaches **done**, **error**, or **cancelled**.
    """
    sk = _task_session_key(key)
    raw = st.session_state.get(sk)
    if raw is None:
        return False
    if not _is_managed_task_box(raw):
        del st.session_state[sk]
        return True
    box = cast(dict[str, Any], raw)

    def is_terminal() -> bool:
        return str(box.get("status")) in ("done", "error", "cancelled")

    if not _with_box_lock(box, is_terminal):
        return False
    del st.session_state[sk]
    return True


def dismiss_tasks(*, keys: Sequence[str]) -> int:
    """Call :func:`dismiss_task` for each key; return how many returned ``True``."""
    n = 0
    for raw in keys:
        key = str(raw).strip()
        if not key:
            raise ValueError("async task key must be a non-empty string")
        if dismiss_task(key=key):
            n += 1
    return n


__all__ = [
    "TaskHandle",
    "complete_cancelled",
    "dismiss_task",
    "dismiss_tasks",
    "is_task_cancel_requested",
    "set_task_progress",
    "submit",
    "submit_many",
]
