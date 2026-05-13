"""Thin enterprise hooks: optional event sink and safe UI strings (no extra pinned deps)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, runtime_checkable

from streamtree.app_context import lookup

EVENT_SINK_KEY = "streamtree_event_sink"


@runtime_checkable
class EventSink(Protocol):
    """App-provided sink for structured events (logging, audit, analytics)."""

    def emit(self, name: str, payload: Mapping[str, Any]) -> None: ...


def emit_event(name: str, payload: Mapping[str, Any] | None = None) -> None:
    """If ``app_context.lookup(EVENT_SINK_KEY)`` returns an :class:`EventSink`, call ``emit``."""
    if not name.strip():
        raise ValueError("event name must be non-empty")
    raw = lookup(EVENT_SINK_KEY)
    if raw is None:
        return
    if isinstance(raw, EventSink):
        raw.emit(name.strip(), dict(payload or {}))


def redact_secrets(text: str, secrets: tuple[str, ...]) -> str:
    """Replace known secret substrings with ``\"[REDACTED]\"`` for safer UI display."""
    out = text
    for s in secrets:
        if s:
            out = out.replace(s, "[REDACTED]")
    return out


def tenant_id(default: str | None = None) -> str | None:
    """Return ``lookup(\"tenant_id\")`` when set as a string (common ``app_context`` convention)."""
    tid = lookup("tenant_id", default=default)
    if tid is None:
        return None
    return str(tid)


__all__ = ["EVENT_SINK_KEY", "EventSink", "emit_event", "redact_secrets", "tenant_id"]
