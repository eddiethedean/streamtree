"""Portal gather and render-time queue (see ``docs/PHASE2_PORTALS_AND_PREFETCH.md``)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from streamtree.core.element import ComponentCall, Element, Fragment
from streamtree.elements.auth_gate import AuthGate
from streamtree.elements.layout import (
    Card,
    Columns,
    Dialog,
    ErrorBoundary,
    Expander,
    Form,
    Grid,
    HStack,
    Page,
    Popover,
    Portal,
    PortalMount,
    Routes,
    Sidebar,
    SplitView,
    Tabs,
    VStack,
)
from streamtree.elements.ui_extra import (
    BottomDock,
    ColoredHeader,
    FloatingActionButton,
    SocialBadge,
    StyleMetricCards,
    VerticalSpaceLines,
)
from streamtree.tables import DataGrid
from streamtree.theme import ThemeRoot

_queue: ContextVar[dict[str, list[Element]] | None] = ContextVar(
    "streamtree_portal_queue", default=None
)


def gather_portals(root: Element) -> dict[str, tuple[Element, ...]]:
    """Collect :class:`Portal` children keyed by slot (depth-first, pre-mount).

    :class:`ComponentCall` nodes are **not** expanded; portals inside unexpanded
    components are invisible until the component runs and returns a tree containing
    them on a later walk (same Streamlit rerun after expansion).
    """
    acc: dict[str, list[Element]] = defaultdict(list)

    def walk(node: Element) -> None:
        if isinstance(node, Portal):
            sk = node.slot.strip()
            acc[sk].append(node.child)
            walk(node.child)
            return
        if isinstance(node, PortalMount):
            return
        if isinstance(node, ComponentCall):
            return
        for ch in _structural_children(node):
            walk(ch)

    walk(root)
    return {k: tuple(v) for k, v in acc.items()}


def _structural_children(node: Element) -> Iterator[Element]:
    if isinstance(node, Fragment):
        yield from node.children
        return
    if isinstance(node, (VStack, HStack, Page, Card, Grid, Columns, Sidebar, Form, Expander)):
        yield from node.children
        return
    if isinstance(node, Tabs):
        for _, ch in node.tabs:
            yield ch
        return
    if isinstance(node, Routes):
        for _, ch in node.routes:
            yield ch
        return
    if isinstance(node, Dialog) or isinstance(node, Popover):
        yield from node.children
        return
    if isinstance(node, ErrorBoundary):
        yield node.child
        yield node.fallback
        return
    if isinstance(node, AuthGate):
        yield node.child
        return
    if isinstance(node, SplitView):
        yield node.narrow
        yield node.main
        return
    if isinstance(node, ThemeRoot):
        return
    if isinstance(node, BottomDock):
        yield from node.children
        return
    if isinstance(
        node, (ColoredHeader, VerticalSpaceLines, SocialBadge, StyleMetricCards, DataGrid)
    ):
        return
    if isinstance(node, FloatingActionButton):
        return
    # Leaf widgets and other Elements: no structural children
    return


@contextmanager
def portal_render_context(root: Element):
    """Install portal queue for one render pass (used by the Streamlit renderer)."""
    gathered = gather_portals(root)
    mutable: dict[str, list[Element]] = {k: list(v) for k, v in gathered.items()}
    token = _queue.set(mutable)
    try:
        yield
    finally:
        _queue.reset(token)


def take_portal_children(slot: str) -> tuple[Element, ...]:
    """Pop all queued children for ``slot`` (first :class:`PortalMount` wins)."""
    sk = slot.strip()
    if not sk:
        return ()
    m = _queue.get()
    if not m:
        return ()
    lst = m.get(sk)
    if not lst:
        return ()
    out = tuple(lst)
    lst.clear()
    return out


__all__ = ["gather_portals", "portal_render_context", "take_portal_children"]
