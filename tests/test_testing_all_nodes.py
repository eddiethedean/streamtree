"""Cover every branch of ``streamtree.testing.render_to_tree``."""

from __future__ import annotations

from streamtree.core.element import fragment
from streamtree.elements import (
    Button,
    Card,
    Checkbox,
    Columns,
    DataFrame,
    Divider,
    ErrorBoundary,
    Expander,
    Form,
    Grid,
    HStack,
    Image,
    Markdown,
    NumberInput,
    Page,
    Routes,
    Selectbox,
    Sidebar,
    Spacer,
    Subheader,
    Tabs,
    Text,
    TextInput,
    ThemeRoot,
    Title,
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
                Selectbox("s", options=["a"]),
                Checkbox("c"),
                DataFrame([]),
                Image("x.png"),
                ErrorBoundary(child=Text("safe"), fallback=Text("fb")),
                Routes(routes=(("home", Text("home body")),), default="home"),
            ),
        )
    )
    assert tree["kind"] == "Page"
    assert len(tree["children"][0]["children"]) >= 20
