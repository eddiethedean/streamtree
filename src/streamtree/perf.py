"""Optional render counters and tree summaries (debug / tests; not a profiler)."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping

from streamtree.app_context import lookup

PERF_COUNTERS_KEY = "streamtree_perf_counters"


def perf_bump(name: str, *, delta: int = 1) -> None:
    """Increment a named counter when ``app_context`` provides ``PERF_COUNTERS_KEY`` → ``dict``.

    No-op if the bag is missing or not a mutable mapping. Intended for lightweight
    instrumentation during development.
    """
    raw = lookup(PERF_COUNTERS_KEY)
    if not isinstance(raw, MutableMapping):
        return
    cur = int(raw.get(name, 0))
    raw[name] = cur + delta


def perf_snapshot() -> dict[str, int]:
    """Return a shallow int copy of counters, or ``{}`` if none."""
    raw = lookup(PERF_COUNTERS_KEY)
    if not isinstance(raw, Mapping):
        return {}
    out: dict[str, int] = {}
    for k, v in raw.items():
        try:
            out[str(k)] = int(v)
        except (TypeError, ValueError):
            continue
    return out


__all__ = ["PERF_COUNTERS_KEY", "perf_bump", "perf_snapshot"]
