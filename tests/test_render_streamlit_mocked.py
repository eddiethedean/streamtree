"""Cover streamtree.renderers.streamlit with a mocked ``st`` (reliable under coverage)."""

from __future__ import annotations

from contextlib import contextmanager, nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from streamtree.core.component import component
from streamtree.core.context import render_context
from streamtree.core.element import ComponentCall, Element
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
    Title,
    VStack,
)
from streamtree.renderers import streamlit as rs
from streamtree.state import FormState, StateVar, form_state, state, toggle_state


def _make_st(
    *,
    container_raises_border: bool = False,
    with_divider_attr: bool = True,
    text_input_side_effect: list[object] | None = None,
    number_input_side_effect: list[object] | None = None,
    selectbox_returns: list[object] | None = None,
    checkbox_returns: list[bool] | None = None,
    button_returns: list[bool] | None = None,
) -> SimpleNamespace:
    st = SimpleNamespace()
    st.session_state = {}

    def container(**kwargs: object) -> object:
        if container_raises_border and kwargs.get("border"):
            raise TypeError("border unsupported")
        return nullcontext()

    st.container = container

    def columns(spec: object, **kwargs: object) -> list[object]:
        if isinstance(spec, (list, tuple)):
            n = len(spec)
        else:
            n = int(spec)  # type: ignore[arg-type]
        return [nullcontext() for _ in range(max(n, 1))]

    st.columns = columns
    st.tabs = lambda labels, **kw: [nullcontext() for _ in labels]
    st.sidebar = nullcontext()
    st.form = lambda *a, **kw: nullcontext()
    st.expander = lambda *a, **kw: nullcontext()
    st.write = MagicMock()
    st.title = MagicMock()
    st.subheader = MagicMock()
    st.markdown = MagicMock()
    st.dataframe = MagicMock()
    st.image = MagicMock()

    if with_divider_attr:
        st.divider = MagicMock()

    btn_iter = iter(button_returns or [False])
    st.button = MagicMock(side_effect=lambda *a, **k: next(btn_iter, False))
    st.form_submit_button = MagicMock(return_value=False)

    ti = text_input_side_effect
    if ti is None:

        def _text_input(**k: object) -> object:
            key = k.get("key")
            if key is not None and key in st.session_state:
                return st.session_state[key]
            return k.get("value", "")

        st.text_input = MagicMock(side_effect=_text_input)
    else:
        st.text_input = MagicMock(side_effect=iter(ti))

    ni = number_input_side_effect
    if ni is None:

        def _number_input(**k: object) -> object:
            key = k.get("key")
            if key is not None and key in st.session_state:
                return st.session_state[key]
            return k.get("value", 0)

        st.number_input = MagicMock(side_effect=_number_input)
    else:
        st.number_input = MagicMock(side_effect=iter(ni))

    sb = selectbox_returns
    if sb is None:
        st.selectbox = MagicMock(
            side_effect=lambda **k: (
                k["options"][min(k.get("index", 0), len(k["options"]) - 1)]
                if k.get("options")
                else None
            )
        )
    else:
        st.selectbox = MagicMock(side_effect=iter(sb))

    cb = checkbox_returns
    if cb is None:

        def _checkbox(**k: object) -> bool:
            key = k.get("key")
            if key is not None and key in st.session_state:
                return bool(st.session_state[key])
            return bool(k.get("value", False))

        st.checkbox = MagicMock(side_effect=_checkbox)
    else:
        st.checkbox = MagicMock(side_effect=iter(cb))

    return st


@contextmanager
def _patched_st(st: SimpleNamespace):
    """Renderer and ``streamtree.state`` must share the same ``session_state`` dict."""
    with patch.object(rs, "st", st), patch("streamtree.state.st", st):
        yield


def test_render_element_full_tree_mocked() -> None:
    st = _make_st()
    png = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06"
        b"\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    @component
    def Inner() -> Element:
        return Text("inner")

    with _patched_st(st):
        with render_context("root"):
            sv_str = state("a", key="svtext")
            sv_num = state(1.0, key="svnum")
            sv_idx = state(0, key="svidx")
            sv_cb = state(False, key="svcb")
            tg = toggle_state(key="tgbind", initial=False)
            fs = form_state("c0", key="fs1")

            tree = Page(
                VStack(
                    Title("T"),
                    Subheader("S"),
                    Text("x"),
                    Markdown("m"),
                    Markdown("raw", unsafe_allow_html=True),
                    Divider(),
                    Inner(),
                    HStack(Text("h1"), Text("h2")),
                    Columns(Text("a"), Text("b"), weights=(1.0,)),
                    Columns(Text("only"), weights=(1.0, 2.0)),
                    Columns(Text("c1"), Text("c2")),
                    Grid(Text("g1"), Text("g2"), Text("g3"), columns=2),
                    Card(Text("card")),
                    Tabs(("t1", Text("a")), ("t2", Text("b"))),
                    Sidebar(Text("sb")),
                    Expander("e", Text("ex"), expanded=True),
                    Spacer(height=3),
                    Spacer(),
                    Form(TextInput("l", value=fs), Button("s", submit=True), form_key="f1"),
                    Button("b", on_click=lambda: None),
                    TextInput("ti", value="plain", key="tik"),
                    TextInput("pw", type="password"),
                    TextInput("bound", value=sv_str),
                    TextInput("keyed", key="widgetkey"),
                    NumberInput(
                        "ni",
                        value=sv_num,
                        min_value=0.0,
                        max_value=9.0,
                        step=0.5,
                        format="%.1f",
                    ),
                    NumberInput("ni2", value=None),
                    NumberInput("nix", value=42),
                    Selectbox("sb", options=["a", "b"], index=sv_idx),
                    Selectbox("sb2", options=["z"], index=0, format_func=lambda x: f"_{x}"),
                    Checkbox("cb", value=sv_cb),
                    Checkbox("cb2", value=tg),
                    Checkbox("cb3", value=True),
                    Checkbox("cb4"),
                    DataFrame({"x": [1]}, width=10, height=20),
                    Image(png, caption="c", width=5, use_column_width=False),
                ),
            )
            rs.render_element(tree)


def test_render_text_input_updates_form_and_statevar() -> None:
    st = _make_st(text_input_side_effect=["new", "new"])
    fs = FormState(_edit_key="e", _committed_key="c", _default="old")
    st.session_state["e"] = "old"
    st.session_state["c"] = "committed"
    sv = StateVar[str](_key="sk", _default="a")
    st.session_state["sk"] = "a"

    with _patched_st(st):
        with render_context("r"):
            rs.render_element(TextInput("f", value=fs), slot="0")
            assert st.session_state["e"] == "new"
            rs.render_element(TextInput("s", value=sv), slot="1")
            assert st.session_state["sk"] == "new"


def test_render_number_input_statevar_updates() -> None:
    st = _make_st(number_input_side_effect=[2.0])
    sv = StateVar[float](_key="nk", _default=1.0)
    st.session_state["nk"] = 1.0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(NumberInput("n", value=sv), slot="0")
            assert st.session_state["nk"] == 2.0


def test_render_selectbox_statevar_updates() -> None:
    st = _make_st(selectbox_returns=["b"])
    sv = StateVar[int](_key="ik", _default=0)
    st.session_state["ik"] = 0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Selectbox("s", options=["a", "b"], index=sv), slot="0")
            assert st.session_state["ik"] == 1


def test_render_selectbox_out_not_in_options() -> None:
    st = _make_st(selectbox_returns=["weird"])
    sv = StateVar[int](_key="ik2", _default=0)
    st.session_state["ik2"] = 0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Selectbox("s", options=["a", "b"], index=sv), slot="0")


def test_render_checkbox_statevar_and_toggle() -> None:
    st = _make_st(checkbox_returns=[True, True])
    sv = StateVar[bool](_key="bk", _default=False)
    st.session_state["bk"] = False
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Checkbox("c", value=sv), slot="0")
            assert st.session_state["bk"] is True
            tg = toggle_state(key="tg2", initial=False)
            rs.render_element(Checkbox("c2", value=tg), slot="1")
            assert st.session_state[tg.key] is True


def test_render_button_click_and_submit() -> None:
    calls: list[int] = []

    def on_click() -> None:
        calls.append(1)

    st = _make_st(button_returns=[True, False])
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Button("x", on_click=on_click), slot="0")
            assert calls == [1]
            rs.render_element(Button("s", submit=True), slot="1")


def test_bordered_container_fallback() -> None:
    st = _make_st(container_raises_border=True)
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Card(Text("c")), slot="0")


def test_divider_without_st_divider() -> None:
    st = _make_st(with_divider_attr=False)
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Divider(), slot="0")
            st.markdown.assert_called()


def test_render_unsupported_element_raises() -> None:
    class Junk(Element):
        pass

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            with pytest.raises(TypeError, match="Unsupported"):
                rs.render_element(Junk(), slot="0")


def test_render_fragment_nested() -> None:
    from streamtree.core.element import fragment

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(fragment(Text("a"), Text("b")), slot="0")


def test_render_grid_empty() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Grid(columns=2), slot="0")


def test_render_hstack_empty() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(HStack(), slot="0")


def test_component_call_with_explicit_key() -> None:
    @component
    def K() -> Element:
        return Text("k")

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(K(key="mykey"), slot="0")


def test_render_component_with_lambda() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            call = ComponentCall(fn=lambda: Text("L"), args=(), kwargs={})
            rs.render_element(call, slot="0")


def test_render_error_boundary_fallback() -> None:
    def boom() -> Element:
        raise RuntimeError("boom")

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(
                ErrorBoundary(
                    child=ComponentCall(fn=boom, args=(), kwargs={}),
                    fallback=Text("recovered"),
                ),
                slot="0",
            )
    st.write.assert_any_call("recovered")


def test_render_error_boundary_on_error_callback() -> None:
    def boom() -> Element:
        raise ValueError("x")

    seen: list[BaseException] = []

    def on_error(exc: BaseException) -> None:
        seen.append(exc)

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(
                ErrorBoundary(
                    child=ComponentCall(fn=boom, args=(), kwargs={}),
                    fallback=Text("fb"),
                    on_error=on_error,
                ),
                slot="0",
            )
    assert len(seen) == 1
    assert isinstance(seen[0], ValueError)


def test_render_routes_selects_active_child() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamtree.renderers.streamlit.sync_route", return_value="two"):
        with render_context("r"):
            rs.render_element(
                Routes(
                    routes=(("one", Text("1")), ("two", Text("2"))),
                    default="one",
                ),
                slot="0",
            )
    st.write.assert_any_call("2")


def test_render_routes_falls_back_to_first_when_default_missing() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamtree.renderers.streamlit.sync_route", return_value="weird"):
        with render_context("r"):
            rs.render_element(
                Routes(routes=(("only", Text("O")),), default="missing"),
                slot="0",
            )
    st.write.assert_any_call("O")


def test_render_routes_unknown_route_falls_back_to_default() -> None:
    st = _make_st()
    with (
        _patched_st(st),
        patch(
            "streamtree.renderers.streamlit.sync_route",
            return_value="missing",
        ),
    ):
        with render_context("r"):
            rs.render_element(
                Routes(routes=(("home", Text("H")),), default="home"),
                slot="0",
            )
    st.write.assert_any_call("H")
