"""Helpers for loading / ready / error UI around :class:`streamtree.asyncio.TaskHandle`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, TypeVar, runtime_checkable

from streamtree.core.element import Element

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
    return loading


__all__ = ["match_task"]
