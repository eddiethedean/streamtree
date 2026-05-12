"""Lightweight dependency-injection bag for the current render (rerun-scoped).

Values are stored in a :class:`contextvars.ContextVar` stack so nested
``provider()`` calls shadow outer keys for their duration. Typical use: wrap
the app root in ``provider(theme=\"dark\")`` and read ``lookup(\"theme\")``
inside descendant components each rerun.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

_bag: ContextVar[dict[str, Any] | None] = ContextVar("streamtree_app_context", default=None)


def _require_key(key: object) -> str:
    if not isinstance(key, str) or not key.strip():
        raise TypeError("app context keys must be non-empty strings")
    return key.strip()


@contextmanager
def provider(**values: Any) -> Iterator[None]:
    """Merge ``values`` into the current bag for the duration of the block."""
    cur = _bag.get()
    nxt = dict(cur) if cur else {}
    for k, v in values.items():
        nxt[_require_key(k)] = v
    token = _bag.set(nxt)
    try:
        yield
    finally:
        _bag.reset(token)


def lookup(key: str, default: Any = None) -> Any:
    """Return a value from the innermost active provider stack, or ``default``."""
    k = _require_key(key)
    cur = _bag.get()
    if not cur:
        return default
    return cur.get(k, default)


def current_bag() -> Mapping[str, Any]:
    """Snapshot of the merged bag (empty mapping if none).

    Returns a shallow copy so mutating the returned dict does not alter
    internal provider state.
    """
    cur = _bag.get()
    if not cur:
        return {}
    return dict(cur)


__all__ = ["current_bag", "lookup", "provider"]
