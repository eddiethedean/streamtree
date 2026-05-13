"""Helpers for loading / ready / error UI around :class:`streamtree.asyncio.TaskHandle`."""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Protocol, TypeVar, runtime_checkable

from streamtree.asyncio import TaskHandle
from streamtree.core.element import Element

_LOGGER = logging.getLogger(__name__)

T_co = TypeVar("T_co", covariant=True)


@runtime_checkable
class _PollableTask(Protocol[T_co]):
    def status(self) -> str: ...
    def result(self) -> T_co | None: ...
    def error(self) -> str | None: ...


def match_task(
    handle: _PollableTask[Any],
    *,
    loading: Element,
    ready: Callable[[Any], Element],
    error: Element,
    cancelled: Element | None = None,
) -> Element:
    """Pick a subtree from a pollable task handle (typically :class:`streamtree.asyncio.TaskHandle`).

    Maps ``pending``, ``running``, and ``missing`` to ``loading``; ``done`` to ``ready(result())``;
    ``error`` to ``error``; ``cancelled`` to ``cancelled`` when provided, otherwise ``error``.
    Any other ``status`` value is treated as ``loading`` and a debug log is emitted (unexpected
    values may indicate a non-StreamTree handle or corrupted task state).
    """
    status = handle.status()
    if status in ("pending", "running", "missing"):
        return loading
    if status == "done":
        return ready(handle.result())
    if status == "error":
        return error
    if status == "cancelled":
        return error if cancelled is None else cancelled
    _LOGGER.debug("match_task: unknown task status %r; using loading branch", status)
    return loading


_KNOWN = frozenset({"pending", "running", "missing", "done", "error", "cancelled"})


def match_task_many(
    handles: Sequence[_PollableTask[Any]],
    *,
    loading: Element,
    ready: Callable[[tuple[Any, ...]], Element],
    error: Element,
    cancelled: Element | None = None,
) -> Element:
    """Pick one subtree from several pollable handles (e.g. :class:`streamtree.asyncio.TaskHandle`).

    **Semantics (fixed order):**

    1. If **any** handle has status ``error``, return ``error``.
    2. Else if **any** has ``cancelled``, return ``cancelled`` when provided, otherwise ``error``.
    3. Else if **any** has ``pending``, ``running``, or ``missing``, return ``loading``.
    4. Else if **any** has an unknown status, log at debug and return ``loading``.
    5. Else (**all** ``done``), return ``ready`` with a tuple of each ``result()`` (``()`` when
       ``handles`` is empty).

    Use after :func:`streamtree.asyncio.submit_many` when the UI should wait for **every**
    task to finish before showing a combined ready branch.
    """
    statuses = [h.status() for h in handles]
    if any(s == "error" for s in statuses):
        return error
    if any(s == "cancelled" for s in statuses):
        return error if cancelled is None else cancelled
    if any(s in ("pending", "running", "missing") for s in statuses):
        return loading
    for s in statuses:
        if s not in _KNOWN:
            _LOGGER.debug("match_task_many: unknown task status %r; using loading branch", s)
            return loading
    return ready(tuple(h.result() for h in handles))


def submit_many_ordered(jobs: Mapping[str, Callable[[], Any]]) -> tuple[TaskHandle[Any], ...]:
    """Start tasks via :func:`streamtree.asyncio.submit_many` in **sorted key order**.

    Returns :class:`~streamtree.asyncio.TaskHandle` instances in **sorted key order**
    (same order as ``sorted(jobs.keys())``). Pass that sequence to :func:`match_task_many`
    so its ``ready`` callback receives ``result()`` values in that same order.
    """
    from streamtree.asyncio import submit_many

    ordered = sorted(jobs.items(), key=lambda kv: kv[0])
    return submit_many([(k, fn) for k, fn in ordered])


__all__ = ["match_task", "match_task_many", "submit_many_ordered"]
