"""Small helpers for list/detail/save flows (see :doc:`PHASE3_CRUD`)."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from streamtree.routing import sync_query_value
from streamtree.state import StateVar, state

T = TypeVar("T")


def selected_id_from_query(*, param: str = "id", default: str = "") -> str:
    """Read a string id (or filter token) from the URL query via :func:`sync_query_value`."""
    return sync_query_value(default, param=param)


def save_intent_counter(*, key: str | None = None) -> tuple[StateVar[int], Callable[[], None]]:
    """Return ``(counter, bump)`` for save workflows: bump from a button ``on_click``; read ``counter()`` on the next rerun to start :func:`streamtree.asyncio.submit`.

    This is the “save_version” pattern from :doc:`PHASE3_CRUD` packaged as a typed pair.
    """
    counter = state(0, key=key)

    def bump() -> None:
        counter.increment(1)

    return counter, bump


__all__ = ["save_intent_counter", "selected_id_from_query"]
