"""Render-time context for stable keys and nested component paths."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field

_ctx: ContextVar[RenderContext | None] = ContextVar("streamtree_render_context", default=None)


@dataclass
class RenderContext:
    """Stacked path segments and a per-scope counter for anonymous state slots."""

    parent: RenderContext | None
    segment: str
    _counter: int = field(default=0, repr=False)

    def child(self, segment: str) -> RenderContext:
        return RenderContext(parent=self, segment=segment)

    def next_anonymous_index(self) -> int:
        i = self._counter
        self._counter += 1
        return i

    def path(self) -> str:
        if self.parent is None:
            return self.segment
        base = self.parent.path()
        return f"{base}.{self.segment}" if base else self.segment


def current_context() -> RenderContext:
    c = _ctx.get()
    if c is None:
        raise RuntimeError("streamtree: no active render context; call from inside render()")
    return c


@contextmanager
def render_context(root_segment: str = "app") -> Iterator[RenderContext]:
    parent = _ctx.get()
    ctx = RenderContext(parent=parent, segment=root_segment) if parent else RenderContext(
        parent=None, segment=root_segment
    )
    token = _ctx.set(ctx)
    try:
        yield ctx
    finally:
        _ctx.reset(token)


@contextmanager
def push_segment(segment: str) -> Iterator[RenderContext]:
    parent = current_context()
    ctx = parent.child(segment)
    token = _ctx.set(ctx)
    try:
        yield ctx
    finally:
        _ctx.reset(token)
