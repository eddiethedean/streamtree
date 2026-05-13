"""Cover streamtree.renderers.streamlit with a mocked ``st`` (reliable under coverage)."""

from __future__ import annotations

import builtins
from contextlib import contextmanager, nullcontext
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from streamtree.auth import AuthGate
from streamtree.core.component import component
from streamtree.core.context import render_context
from streamtree.core.element import ComponentCall, Element
from streamtree.elements import (
    Button,
    Card,
    Checkbox,
    ColoredHeader,
    Columns,
    Chart,
    DataFrame,
    DataGrid,
    Dialog,
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
    PageLink,
    Popover,
    Routes,
    Selectbox,
    Sidebar,
    SocialBadge,
    Spacer,
    StyleMetricCards,
    Subheader,
    Tabs,
    Text,
    TextInput,
    Title,
    VerticalSpaceLines,
    VStack,
)
from streamtree.renderers import streamlit as rs
from streamtree.state import FormState, StateVar, form_state, state, toggle_state
from streamtree.theme import ThemeRoot


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
    st.plotly_chart = MagicMock()

    if with_divider_attr:
        st.divider = MagicMock()

    btn_iter = iter(button_returns or [False])
    st.button = MagicMock(side_effect=lambda *a, **k: next(btn_iter, False))
    st.form_submit_button = MagicMock(return_value=False)

    st.page_link = MagicMock()

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

        def _selectbox(**k: object) -> object:
            opts = k.get("options")
            if not opts:
                return None
            raw_i = k.get("index", 0)
            i = int(raw_i) if isinstance(raw_i, (int, float)) else 0
            i = min(max(i, 0), len(opts) - 1)
            ff = k.get("format_func")
            if callable(ff):
                ff(opts[i])
            return opts[i]

        st.selectbox = MagicMock(side_effect=_selectbox)
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

    st.dialog = lambda title: lambda fn: fn
    st.popover = lambda *a, **kw: nullcontext()
    st.warning = MagicMock()

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
                    Columns(Text("a"), Text("b"), weights=(1.0, 1.0)),
                    Columns(Text("only"), weights=(1.0,)),
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
                    PageLink("Other", page="pages/other.py", icon="🔭"),
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
            assert st.page_link.called


def test_render_page_link_minimal_and_full_kwargs() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("pl"):
            rs.render_element(PageLink("Home", page="app.py"), slot="0")
            st.page_link.assert_called_with(page="app.py", label="Home", disabled=False)
            st.page_link.reset_mock()
            rs.render_element(
                PageLink(
                    "Docs",
                    page="docs.py",
                    icon="📖",
                    help="Open docs",
                    use_container_width=True,
                ),
                slot="1",
            )
            st.page_link.assert_called_with(
                page="docs.py",
                label="Docs",
                disabled=False,
                icon="📖",
                help="Open docs",
                use_container_width=True,
            )


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


def test_render_number_input_formstate_updates() -> None:
    st = _make_st(number_input_side_effect=[3.0])
    fs = FormState(_edit_key="ne", _committed_key="nc", _default=1.0)
    st.session_state["ne"] = 1.0
    st.session_state["nc"] = 1.0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(NumberInput("f", value=fs), slot="0")
            assert st.session_state["ne"] == 3.0


def test_render_number_input_optional_statevar_updates() -> None:
    st = _make_st(number_input_side_effect=[9.0])
    with _patched_st(st):
        with render_context("r"):
            sv = state(None, key="onz")
            assert sv() is None
            rs.render_element(NumberInput("n", value=sv), slot="0")
            assert st.session_state[sv.key] == 9.0


def test_render_image_use_container_width_kw() -> None:
    st = _make_st()
    png = b"x"
    with _patched_st(st), render_context("im"):
        rs.render_element(Image(png, use_container_width=True), slot="0")
    st.image.assert_called_once_with(png, use_container_width=True)


def test_render_image_use_column_width_kw() -> None:
    st = _make_st()
    png = b"y"
    with _patched_st(st), render_context("im2"):
        rs.render_element(Image(png, use_column_width="auto"), slot="0")
    st.image.assert_called_once_with(png, use_column_width="auto")


def test_render_selectbox_statevar_updates() -> None:
    st = _make_st(selectbox_returns=[1])
    sv = StateVar[int](_key="ik", _default=0)
    st.session_state["ik"] = 0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Selectbox("s", options=["a", "b"], index=sv), slot="0")
            assert st.session_state["ik"] == 1


def test_render_selectbox_duplicate_options_statevar_syncs_by_index() -> None:
    """StateVar-bound selectbox uses internal indices so duplicate option values stay distinct."""
    st = _make_st(selectbox_returns=[1])
    sv = StateVar[int](_key="dupidx", _default=0)
    st.session_state["dupidx"] = 0
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(Selectbox("s", options=["x", "x"], index=sv), slot="0")
            assert st.session_state["dupidx"] == 1


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


def test_render_hstack_empty_with_gap_uses_non_empty_column_spec() -> None:
    st = _make_st()
    recorded: list[list[float]] = []

    def columns_capture(spec: object, **kwargs: object) -> list[object]:
        if isinstance(spec, (list, tuple)):
            recorded.append([float(x) for x in spec])
            n = len(spec)
        else:
            n = int(spec)  # type: ignore[arg-type]
        return [nullcontext() for _ in range(max(n, 1))]

    st.columns = columns_capture
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(HStack(gap="8px"), slot="0")
    assert recorded == [[1.0]]


def test_component_call_with_explicit_key() -> None:
    @component
    def K() -> Element:
        return Text("k")

    st = _make_st()
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(K(key="mykey"), slot="0")


def test_render_hstack_with_gap_inserts_gutter_columns() -> None:
    st = _make_st()
    recorded: list[list[float]] = []

    def columns_capture(spec: object, **kwargs: object) -> list[object]:
        if isinstance(spec, (list, tuple)):
            recorded.append([float(x) for x in spec])
            n = len(spec)
        else:
            n = int(spec)  # type: ignore[arg-type]
        return [nullcontext() for _ in range(max(n, 1))]

    st.columns = columns_capture
    with _patched_st(st):
        with render_context("r"):
            rs.render_element(HStack(Text("a"), Text("b"), gap="8px"), slot="0")
    assert recorded == [[1.0, 0.12, 1.0]]


def test_render_component_returns_none_raises() -> None:
    @component
    def N() -> Element:
        return None  # type: ignore[return-value]

    st = _make_st()
    with _patched_st(st), render_context("r"), pytest.raises(TypeError, match="returned None"):
        rs.render_element(N(), slot="0")


def test_render_component_returns_bad_type_raises() -> None:
    @component
    def W() -> Element:
        return 99  # type: ignore[return-value]

    st = _make_st()
    with _patched_st(st), render_context("r"), pytest.raises(TypeError, match="int"):
        rs.render_element(W(), slot="0")


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

    seen: list[Exception] = []

    def on_error(exc: Exception) -> None:
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


def test_render_error_boundary_on_error_raises_still_shows_fallback() -> None:
    def boom() -> Element:
        raise RuntimeError("child boom")

    st = _make_st()

    def on_error(_exc: Exception) -> None:
        raise RuntimeError("callback boom")

    with _patched_st(st):
        with render_context("r"):
            rs.render_element(
                ErrorBoundary(
                    child=ComponentCall(fn=boom, args=(), kwargs={}),
                    fallback=Text("still here"),
                    on_error=on_error,
                ),
                slot="0",
            )
    st.write.assert_any_call("still here")


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


def test_render_routes_unknown_active_falls_back_to_default_child() -> None:
    """When ``sync_route`` returns a name not in the map, renderer uses ``default``'s subtree."""
    st = _make_st()
    with _patched_st(st), patch("streamtree.renderers.streamlit.sync_route", return_value="weird"):
        with render_context("r"):
            rs.render_element(
                Routes(
                    routes=(("home", Text("H")), ("about", Text("A"))),
                    default="home",
                ),
                slot="0",
            )
    st.write.assert_any_call("H")


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


def test_render_theme_root_injects_css() -> None:
    st = _make_st()
    with _patched_st(st), render_context("tr"):
        rs.render_element(ThemeRoot(), slot="0")
    st.markdown.assert_called_once()
    arg0 = st.markdown.call_args[0][0]
    assert "<style>" in arg0
    assert "--st-theme-primary" in arg0


def test_selectbox_empty_options_raises() -> None:
    with pytest.raises(ValueError, match="at least one option"):
        Selectbox("label", options=())


def test_render_dialog_open_invokes_body() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("dlg"):
            rs.render_element(Dialog("T", Text("inside"), open=True), slot="0")
    st.write.assert_any_call("inside")


def test_render_dialog_closed_is_noop() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("dlg2"):
            rs.render_element(Dialog("T", Text("inside"), open=False), slot="0")
    st.write.assert_not_called()


def test_render_dialog_without_st_dialog_warns_and_inlines() -> None:
    st = _make_st()
    del st.dialog
    with _patched_st(st):
        with render_context("dlg3"):
            rs.render_element(Dialog("T", Text("fb"), open=True), slot="0")
    st.warning.assert_called_once()
    st.write.assert_any_call("fb")


def test_render_popover_renders_children() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("pop"):
            rs.render_element(Popover("More", Text("pbody")), slot="0")
    st.write.assert_any_call("pbody")


def test_render_popover_expander_fallback() -> None:
    st = _make_st()
    del st.popover
    with _patched_st(st):
        with render_context("pop2"):
            rs.render_element(Popover("M", Text("exb")), slot="0")
    st.write.assert_any_call("exb")


def test_render_auth_gate_shows_child_when_authenticated() -> None:
    st = _make_st()

    class FakeAuth:
        def login(self, **kwargs: object) -> None:
            st.session_state["authentication_status"] = True

    cfg = {
        "credentials": {"usernames": {}},
        "cookie": {"name": "c", "key": "secretkey", "expiry_days": 1},
    }
    with _patched_st(st), patch("streamtree.auth.build_authenticator", return_value=FakeAuth()):
        with render_context("ag"):
            rs.render_element(AuthGate(config=cfg, child=Text("secret")), slot="0")
    st.write.assert_any_call("secret")


def test_render_auth_gate_missing_dependency_raises() -> None:
    st = _make_st()
    with (
        _patched_st(st),
        patch(
            "streamtree.auth.build_authenticator",
            side_effect=ImportError("no auth"),
        ),
    ):
        with render_context("ag2"), pytest.raises(ImportError, match="streamtree\\[auth\\]"):
            rs.render_element(
                AuthGate(
                    config={"credentials": {}, "cookie": {"name": "n", "key": "k"}},
                    child=Text("x"),
                ),
                slot="0",
            )


def test_render_colored_header_delegates() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamlit_extras.colored_header.colored_header") as ch:
        with render_context("ch"):
            rs.render_element(ColoredHeader("L", description="D", color_name="green-70"), slot="0")
    ch.assert_called_once_with("L", description="D", color_name="green-70")


def test_render_colored_header_missing_ui_extra_raises() -> None:
    st = _make_st()
    with (
        _patched_st(st),
        patch(
            "streamlit_extras.colored_header.colored_header",
            side_effect=ImportError("nope"),
        ),
    ):
        with render_context("ch2"), pytest.raises(ImportError, match="streamtree\\[ui\\]"):
            rs.render_element(ColoredHeader("L"), slot="0")


def test_render_vertical_space_lines_delegates() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamlit_extras.add_vertical_space.add_vertical_space") as av:
        with render_context("vs"):
            rs.render_element(VerticalSpaceLines(3), slot="0")
    av.assert_called_once_with(3)


def test_render_dialog_open_with_toggle_state() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("tg"):
            tg = toggle_state(key="dlgopen", initial=True)
            rs.render_element(Dialog("T", Text("tog"), open=tg), slot="0")
    st.write.assert_any_call("tog")


def test_render_dialog_open_with_statevar() -> None:
    st = _make_st()
    with _patched_st(st):
        with render_context("svdlg"):
            op = state(True, key="dlgsv")
            rs.render_element(Dialog("T", Text("stvar"), open=op), slot="0")
    st.write.assert_any_call("stvar")


def test_render_vertical_space_import_error() -> None:
    st = _make_st()
    with (
        _patched_st(st),
        patch(
            "streamlit_extras.add_vertical_space.add_vertical_space",
            side_effect=ImportError("nope"),
        ),
    ):
        with render_context("vs2"), pytest.raises(ImportError, match="streamtree\\[ui\\]"):
            rs.render_element(VerticalSpaceLines(), slot="0")


def test_render_social_badge_delegates() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamlit_extras.badges.badge") as mock_badge:
        with render_context("sb"):
            rs.render_element(SocialBadge(kind="pypi", name="streamtree"), slot="0")
        mock_badge.assert_called_once_with("pypi", name="streamtree", url=None)


def test_render_style_metric_cards_delegates() -> None:
    st = _make_st()
    with _patched_st(st), patch("streamlit_extras.metric_cards.style_metric_cards") as smc:
        with render_context("mc"):
            rs.render_element(StyleMetricCards(border_left_color="#ff0000"), slot="0")
        smc.assert_called_once()
        assert smc.call_args.kwargs["border_left_color"] == "#ff0000"


def test_render_social_badge_import_error_message() -> None:
    st = _make_st()
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "streamlit_extras.badges":
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with _patched_st(st), patch.object(builtins, "__import__", side_effect=_fake):
        with render_context("sbie"), pytest.raises(ImportError, match="streamtree\\[ui\\]"):
            rs.render_element(SocialBadge(kind="pypi", name="z"), slot="0")


def test_render_style_metric_cards_import_error_message() -> None:
    st = _make_st()
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "streamlit_extras.metric_cards":
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with _patched_st(st), patch.object(builtins, "__import__", side_effect=_fake):
        with render_context("mcie"), pytest.raises(ImportError, match="streamtree\\[ui\\]"):
            rs.render_element(StyleMetricCards(), slot="0")


def test_render_datagrid_and_chart_delegate_to_helpers() -> None:
    st = _make_st()
    fig = MagicMock()
    with _patched_st(st):
        with (
            patch("streamtree.tables.render_datagrid") as rd,
            patch("streamtree.charts.render_chart") as rc,
        ):
            with render_context("p3"):
                rs.render_element(
                    Page(VStack(DataGrid([{"a": 1}], key="g1"), Chart(fig, key="c1"))),
                )
        rd.assert_called_once()
        rc.assert_called_once()
