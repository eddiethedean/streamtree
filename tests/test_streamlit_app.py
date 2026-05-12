"""End-to-end render coverage via Streamlit AppTest."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest


def _coverage_app() -> None:
    import base64

    from streamtree import component, render
    from streamtree.core.element import fragment
    from streamtree.elements import (
        Button,
        Card,
        Checkbox,
        Columns,
        DataFrame,
        Divider,
        Expander,
        Form,
        Grid,
        HStack,
        Image,
        Markdown,
        NumberInput,
        Page,
        Selectbox,
        Sidebar,
        Spacer,
        Subheader,
        Tabs,
        Text,
        TextInput,
        Title,
        VStack,
    )
    from streamtree.state import form_state, state, toggle_state

    png_1x1 = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )

    @component
    def Inner() -> object:
        return Text("inner-component")

    fs = form_state("start", key="formtext")
    n = state(3.0, key="numbind")
    idx = state(0, key="selidx")
    cb = state(True, key="cbbind")
    tg = toggle_state(key="tgbind", initial=False)

    tree = Page(
        VStack(
            Title("T"),
            Subheader("S"),
            Text("body"),
            Markdown("# md", unsafe_allow_html=False),
            Markdown("<b>x</b>", unsafe_allow_html=True),
            Divider(),
            fragment(Text("in-frag")),
            Inner(),
            HStack(Text("a"), Text("b")),
            Columns(Text("c1"), Text("c2"), weights=(2.0, 1.0)),
            Columns(Text("only"), weights=(1.0, 2.0, 3.0)),
            Grid(Text("g1"), Text("g2"), Text("g3"), columns=2),
            Card(Text("in-card")),
            Tabs(("tab1", Text("one")), ("tab2", Text("two"))),
            Sidebar(Text("side")),
            Expander("ex", Text("hidden"), expanded=False),
            Spacer(height=4),
            Spacer(),
            Form(
                TextInput("f", value=fs),
                Button("Submit", submit=True),
                form_key="fk",
            ),
            Form(
                TextInput("plain", value="hello"),
                Button("Go", submit=True),
                form_key="fk2",
            ),
            Button("click", on_click=lambda: None, key="btnk"),
            TextInput("pw", type="password"),
            TextInput("bound", value=state("x", key="tib")),
            NumberInput("n", value=n, min_value=0.0, max_value=10.0, step=0.5, format="%.1f"),
            NumberInput("n2", value=None),
            Selectbox("sb", options=["a", "b"], index=idx, format_func=lambda x: x.upper()),
            Selectbox("sb2", options=["x"], index=0),
            Checkbox("c", value=cb),
            Checkbox("c2", value=tg),
            Checkbox("c3", value=False),
            Checkbox("c4"),
            DataFrame({"col": [1, 2]}, width=100, height=50),
            Image(png_1x1, caption="cap", width=10, use_column_width=False),
            key="pagek",
        ),
    )
    render(tree)


def test_full_streamlit_tree_app() -> None:
    at = AppTest.from_function(_coverage_app).run(timeout=20)
    assert not at.exception


def test_state_outside_render_raises_in_app() -> None:
    def bad() -> None:
        from streamtree.core.context import render_context
        from streamtree.state import state

        with render_context("x"):
            state(0)

        state(1)

    at = AppTest.from_function(bad).run(timeout=20)
    assert at.exception is not None
