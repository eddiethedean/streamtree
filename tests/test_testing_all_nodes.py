"""Cover every branch of ``streamtree.testing.render_to_tree``."""

from __future__ import annotations

from streamtree.auth import AuthGate
from streamtree.core.element import fragment
from streamtree.elements import (
    BottomDock,
    Button,
    Card,
    Checkbox,
    ColoredHeader,
    Columns,
    Chart,
    AltairChart,
    EChartsChart,
    DataFrame,
    DataGrid,
    Dialog,
    Divider,
    ErrorBoundary,
    Expander,
    FloatingActionButton,
    Form,
    Grid,
    HStack,
    Image,
    Markdown,
    MentionChip,
    NumberInput,
    Page,
    PageLink,
    Popover,
    Portal,
    PortalMount,
    Routes,
    Selectbox,
    Sidebar,
    SocialBadge,
    Spacer,
    SplitView,
    Stoggle,
    StyleMetricCards,
    Subheader,
    Tabs,
    TaggerRow,
    Text,
    TextInput,
    ThemeRoot,
    Title,
    VerticalSpaceLines,
    VStack,
)
from streamtree.state import StateVar
from streamtree.testing import render_to_tree


def test_render_to_tree_exercises_all_node_types() -> None:
    """One shallow instance per kind so ``_node`` hits each arm."""
    sv = StateVar(_key="k", _default="v")
    tree = render_to_tree(
        Page(
            VStack(
                ThemeRoot(),
                fragment(Text("f")),
                HStack(Text("h")),
                Columns(Text("c1"), weights=(1.0,)),
                Grid(Text("g"), columns=1),
                Card(Text("card")),
                Tabs(("t", Text("tab"))),
                Sidebar(Text("sb")),
                Form(Text("in"), form_key="fk"),
                Expander("ex", Text("e")),
                Spacer(height=1),
                Spacer(),
                Text("t"),
                Title("ti"),
                Subheader("su"),
                Markdown("m"),
                Divider(),
                Button("b"),
                TextInput("ti", value=sv),
                NumberInput("n"),
                PageLink("Go", page="pages/1_Home.py"),
                Selectbox("s", options=["a"]),
                Checkbox("c"),
                DataFrame([]),
                DataGrid([], key="dg"),
                Chart(object(), key="ch"),
                AltairChart(object(), key="ac"),
                EChartsChart({"series": []}, key="ec"),
                Image("x.png"),
                ErrorBoundary(child=Text("safe"), fallback=Text("fb")),
                Routes(routes=(("home", Text("home body")),), default="home"),
                Dialog("dlg", Text("d"), open=True),
                Popover("pop", Text("pv")),
                AuthGate(
                    config={"credentials": {}, "cookie": {"name": "n", "key": "k"}},
                    child=Text("authed"),
                ),
                ColoredHeader("CH"),
                SocialBadge(kind="pypi", name="pkg"),
                StyleMetricCards(),
                VerticalSpaceLines(2),
                SplitView(narrow=Text("nav"), main=Text("main")),
                PortalMount(slot="z"),
                Portal(slot="z", child=Text("portal child")),
                BottomDock(Text("dock")),
                FloatingActionButton("fab", key="faball"),
                Stoggle("sum", "content"),
                TaggerRow("c", ("t",)),
                MentionChip("L", "https://example.invalid"),
            ),
        )
    )
    assert tree["kind"] == "Page"
    assert len(tree["children"][0]["children"]) >= 29
