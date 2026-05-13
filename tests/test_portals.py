"""Tests for streamtree.portals gather and mount semantics."""

from __future__ import annotations

from streamtree.elements import (
    AuthGate,
    BottomDock,
    DeferredFragment,
    Dialog,
    ErrorBoundary,
    Page,
    Popover,
    Portal,
    PortalMount,
    Routes,
    SplitView,
    Text,
    VStack,
)
from streamtree.portals import gather_portals, portal_render_context, take_portal_children
from streamtree.theme import ThemeRoot


def test_gather_portals_orders_by_tree_dfs() -> None:
    tree = Page(
        VStack(
            Portal(slot="a", child=Text("1")),
            Portal(slot="a", child=Text("2")),
            PortalMount(slot="a"),
        )
    )
    g = gather_portals(tree)
    assert g["a"] == (Text("1"), Text("2"))


def test_take_portal_children_consumes_once() -> None:
    tree = Page(VStack(Portal(slot="x", child=Text("only"))))
    with portal_render_context(tree):
        assert take_portal_children("x") == (Text("only"),)
        assert take_portal_children("x") == ()


def test_take_portal_children_blank_slot_returns_empty() -> None:
    tree = Page(Text("x"))
    with portal_render_context(tree):
        assert take_portal_children("   ") == ()


def test_take_portal_children_outside_context_returns_empty() -> None:
    assert take_portal_children("any") == ()


def test_take_portal_children_unknown_slot_returns_empty() -> None:
    tree = Page(PortalMount(slot="empty"))
    with portal_render_context(tree):
        assert take_portal_children("empty") == ()


def test_gather_portals_walks_routes_errorboundary_auth_split_bottom() -> None:
    tree = Page(
        VStack(
            Routes(
                routes=(("home", Portal(slot="rt", child=Text("r"))),),
                default="home",
            ),
            ErrorBoundary(
                child=Portal(slot="eb_c", child=Text("try")),
                fallback=Portal(slot="eb_f", child=Text("fail")),
            ),
            AuthGate(config={}, child=Portal(slot="ag", child=Text("in"))),
            SplitView(
                narrow=Portal(slot="sv", child=Text("nav")),
                main=Text("body"),
            ),
            BottomDock(Portal(slot="bd", child=Text("pin"))),
        )
    )
    g = gather_portals(tree)
    assert g["rt"] == (Text("r"),)
    assert g["eb_c"] == (Text("try"),)
    assert g["eb_f"] == (Text("fail"),)
    assert g["ag"] == (Text("in"),)
    assert g["sv"] == (Text("nav"),)
    assert g["bd"] == (Text("pin"),)


def test_gather_portals_walks_dialog_popover_theme_root() -> None:
    tree = Page(
        VStack(
            ThemeRoot(),
            Dialog("D", Portal(slot="dlg", child=Text("modal"))),
            Popover("P", Portal(slot="pop", child=Text("panel"))),
        )
    )
    g = gather_portals(tree)
    assert g["dlg"] == (Text("modal"),)
    assert g["pop"] == (Text("panel"),)


def test_gather_portals_walks_deferred_fragment() -> None:
    tree = Page(
        VStack(
            DeferredFragment(
                Portal(slot="df", child=Text("deferred")),
                PortalMount(slot="df"),
            ),
        )
    )
    g = gather_portals(tree)
    assert g["df"] == (Text("deferred"),)


def test_gather_portals_nested_deferred_fragments() -> None:
    tree = Page(
        DeferredFragment(
            DeferredFragment(Portal(slot="n", child=Text("deep"))),
        )
    )
    g = gather_portals(tree)
    assert g["n"] == (Text("deep"),)


def test_gather_portals_deferred_then_sibling_same_slot_order() -> None:
    """DFS order: inner ``DeferredFragment`` portal before sibling ``Portal``."""
    tree = Page(
        VStack(
            DeferredFragment(Portal(slot="q", child=Text("first"))),
            Portal(slot="q", child=Text("second")),
        )
    )
    g = gather_portals(tree)
    assert g["q"] == (Text("first"), Text("second"))


def test_portal_render_context_deferred_fragment_delivers_to_mount() -> None:
    tree = Page(
        VStack(
            DeferredFragment(Portal(slot="slot", child=Text("payload"))),
            PortalMount(slot="slot"),
        )
    )
    with portal_render_context(tree):
        assert take_portal_children("slot") == (Text("payload"),)
        assert take_portal_children("slot") == ()
