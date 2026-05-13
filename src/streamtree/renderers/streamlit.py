"""Streamlit backend: maps the virtual element tree to ``st`` calls."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, cast

import streamlit as st

from streamtree.core.context import current_context, push_segment
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
    Spacer,
    SplitView,
    Tabs,
    VStack,
)
from streamtree.elements.ui_extra import (
    BottomDock,
    ColoredHeader,
    FloatingActionButton,
    MentionChip,
    SocialBadge,
    StyleMetricCards,
    Stoggle,
    TaggerRow,
    VerticalSpaceLines,
)
from streamtree.elements.widgets import (
    Button,
    Checkbox,
    DataFrame,
    Divider,
    Image,
    Markdown,
    NumberInput,
    PageLink,
    Selectbox,
    Subheader,
    Text,
    TextInput,
    Title,
)
from streamtree.routing import sync_route
from streamtree.state import FormState, StateVar, ToggleState
from streamtree.theme import ThemeRoot, theme_css

__all__ = ["render", "render_element"]

_DG_TYPE: type | None = None
_CHART_TYPE: type | None = None


def _datagrid_type() -> type:
    global _DG_TYPE
    if _DG_TYPE is None:
        from streamtree.tables import DataGrid

        _DG_TYPE = DataGrid
    return _DG_TYPE


def _chart_type() -> type:
    global _CHART_TYPE
    if _CHART_TYPE is None:
        from streamtree.charts import Chart

        _CHART_TYPE = Chart
    return _CHART_TYPE


def _coerce_open_flag(open_v: object) -> bool:
    from streamtree.state import StateVar, ToggleState

    if isinstance(open_v, StateVar):
        return bool(open_v())
    if isinstance(open_v, ToggleState):
        return bool(open_v())
    return bool(open_v)


def _ensure_component_result(tree: object, fn: Callable[..., Any]) -> Element:
    name = getattr(fn, "__name__", "component")
    if tree is None:
        raise TypeError(
            f"component {name!r} returned None; expected an Element (e.g. Page, VStack, fragment())"
        )
    if not isinstance(tree, Element):
        raise TypeError(f"component {name!r} returned {type(tree)!r}; expected an Element subclass")
    return tree


def _maybe_bordered_container() -> Any:
    """Prefer bordered containers when Streamlit supports them."""
    try:
        return st.container(border=True)  # type: ignore[call-arg]
    except TypeError:
        return st.container()


def _widget_key(el: Element, role: str, slot: str) -> str:
    if el.key:
        return f"streamtree.widget.{el.key}"
    return f"streamtree.{current_context().path()}.{slot}.{role}"


def _render_text_input(el: TextInput, slot: str) -> None:
    val = el.value
    kwargs: dict[str, Any] = {
        "label": el.label,
        "disabled": el.disabled,
        "placeholder": el.placeholder or "",
    }
    if el.type == "password":
        kwargs["type"] = "password"

    if isinstance(val, FormState):
        fs = cast(FormState[str], val)
        kwargs["key"] = fs.edit_key
        # Edit buffer is initialized in ``form_state()``; passing ``value=`` as well
        # triggers Streamlit's session-state policy error and can hang AppTest.
        out = st.text_input(**kwargs)
        if out != fs.edit_value():
            fs.set_edit(out)
        return

    if isinstance(val, StateVar):
        sv = cast(StateVar[str], val)
        kwargs["key"] = sv.key
        out = st.text_input(**kwargs)
        if out != sv():
            sv.set(out)
        return

    kwargs["key"] = _widget_key(el, "text_input", slot)
    if isinstance(val, str):
        kwargs["value"] = val
    st.text_input(**kwargs)


def _render_number_input(el: NumberInput, slot: str) -> None:
    val = el.value
    kwargs: dict[str, Any] = {
        "label": el.label,
        "disabled": el.disabled,
    }
    if el.min_value is not None:
        kwargs["min_value"] = el.min_value
    if el.max_value is not None:
        kwargs["max_value"] = el.max_value
    if el.step is not None:
        kwargs["step"] = el.step
    if el.format is not None:
        kwargs["format"] = el.format

    if isinstance(val, FormState):
        fs = cast(FormState[Any], val)
        kwargs["key"] = fs.edit_key
        out = st.number_input(**kwargs)
        if out != fs.edit_value():
            fs.set_edit(cast(Any, out))
        return

    if isinstance(val, StateVar):
        kwargs["key"] = val.key
        out = st.number_input(**kwargs)
        if out != val():
            val.set(cast(Any, out))
        return

    kwargs["key"] = _widget_key(el, "number_input", slot)
    if val is not None:
        kwargs["value"] = val
    else:
        kwargs["value"] = None
    st.number_input(**kwargs)


def _render_selectbox(el: Selectbox, slot: str) -> None:
    opts = list(el.options)
    idx = el.index
    if isinstance(idx, StateVar):
        idx_sv = cast(StateVar[int], idx)
        wk = _widget_key(el, "selectbox", slot)
        i = int(idx_sv())
        bound = min(max(i, 0), max(len(opts) - 1, 0))
        internal = list(range(len(opts)))
        fmt = el.format_func
        if fmt is not None:

            def _fmt(j: int) -> str:
                return str(fmt(opts[int(j)]))

            format_func: Callable[[Any], str] = _fmt
        else:

            def _fmt_plain(j: int) -> str:
                return str(opts[int(j)])

            format_func = _fmt_plain
        out = st.selectbox(
            label=el.label,
            options=internal,
            index=bound,
            format_func=format_func,
            disabled=el.disabled,
            key=wk,
        )
        new_i = int(out) if isinstance(out, int) else bound
        if 0 <= new_i < len(opts) and new_i != i:
            idx_sv.set(new_i)
        return

    kwargs: dict[str, Any] = {
        "label": el.label,
        "options": opts,
        "disabled": el.disabled,
    }
    if el.format_func is not None:
        kwargs["format_func"] = el.format_func

    kwargs["key"] = _widget_key(el, "selectbox", slot)
    if isinstance(idx, int):
        kwargs["index"] = min(max(idx, 0), max(len(opts) - 1, 0))
    st.selectbox(**kwargs)


def _render_checkbox(el: Checkbox, slot: str) -> None:
    kwargs: dict[str, Any] = {"label": el.label, "disabled": el.disabled}
    val = el.value
    if isinstance(val, (StateVar, ToggleState)):
        kwargs["key"] = val.key
        out = st.checkbox(**kwargs)
        if out != bool(val()):
            val.set(out)
        return
    kwargs["key"] = _widget_key(el, "checkbox", slot)
    if val is not None:
        kwargs["value"] = val
    st.checkbox(**kwargs)


def render_element(el: Element, *, slot: str = "0") -> None:
    """Render a single element and its descendants."""
    if isinstance(el, Fragment):
        for i, ch in enumerate(el.children):
            render_element(ch, slot=f"{slot}.f{i}")
        return

    if isinstance(el, ThemeRoot):
        st.markdown(
            f"<style>{theme_css()}</style>",
            unsafe_allow_html=True,
        )
        return

    if isinstance(el, ComponentCall):
        seg = el.key or getattr(el.fn, "__name__", "component")
        with push_segment(seg):
            tree = el.fn(*el.args, **el.kwargs)
        render_element(_ensure_component_result(tree, el.fn), slot=slot)
        return

    if isinstance(el, VStack):
        for i, ch in enumerate(el.children):
            render_element(ch, slot=f"{slot}.v{i}")
        return

    if isinstance(el, Page):
        for i, ch in enumerate(el.children):
            render_element(ch, slot=f"{slot}.p{i}")
        return

    if isinstance(el, HStack):
        children = list(el.children)
        n = len(children)
        gap = (el.gap or "").strip()
        if not gap:
            cols = st.columns([1] * max(n, 1))
            for i, ch in enumerate(children):
                with cols[i]:
                    render_element(ch, slot=f"{slot}.h{i}")
            return
        if n == 0:
            # Match no-gap empty HStack: never call ``st.columns`` with an empty weight list.
            st.columns([1.0])
            return
        weights: list[float] = []
        for i in range(n):
            weights.append(1.0)
            if i < n - 1:
                weights.append(0.12)
        cols = st.columns(weights)
        col_idx = 0
        for i, ch in enumerate(children):
            with cols[col_idx]:
                render_element(ch, slot=f"{slot}.h{i}")
            col_idx += 1
            if i < n - 1:
                with cols[col_idx]:
                    st.markdown(
                        f"<div aria-hidden='true' style='min-width:{gap};height:1px'></div>",
                        unsafe_allow_html=True,
                    )
                col_idx += 1
        return

    if isinstance(el, Columns):
        n = max(len(el.children), 1)
        weights = list(el.weights) if el.weights else [1.0] * n
        cols = st.columns(weights)
        for i, ch in enumerate(el.children):
            with cols[i]:
                render_element(ch, slot=f"{slot}.col{i}")
        return

    if isinstance(el, Grid):
        cols_n = el.columns
        rows: list[list[Element]] = []
        row: list[Element] = []
        for ch in el.children:
            row.append(ch)
            if len(row) >= cols_n:
                rows.append(row)
                row = []
        if row:
            rows.append(row)
        for ri, r in enumerate(rows):
            cols = st.columns([1] * cols_n)
            for ci, ch in enumerate(r):
                with cols[ci]:
                    render_element(ch, slot=f"{slot}.g{ri}_{ci}")
        return

    if isinstance(el, Card):
        with _maybe_bordered_container():
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.card{i}")
        return

    if isinstance(el, Tabs):
        labels = [t[0] for t in el.tabs]
        panels = st.tabs(labels)
        for i, (_, child) in enumerate(el.tabs):
            with panels[i]:
                render_element(child, slot=f"{slot}.t{i}")
        return

    if isinstance(el, Sidebar):
        with st.sidebar:
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.sb{i}")
        return

    if isinstance(el, Form):
        with st.form(el.form_key, clear_on_submit=el.clear_on_submit):
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.form{i}")
        return

    if isinstance(el, Expander):
        with st.expander(el.label, expanded=el.expanded):
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.ex{i}")
        return

    if isinstance(el, Spacer):
        if el.height:
            st.markdown(f"<div style='height:{el.height}px'></div>", unsafe_allow_html=True)
        else:
            st.write("")
        return

    if isinstance(el, ErrorBoundary):
        try:
            render_element(el.child, slot=f"{slot}.eb_c")
        except Exception as exc:
            if el.on_error is not None:
                try:
                    el.on_error(exc)
                except Exception as cb_exc:
                    logging.getLogger("streamtree.render").error(
                        "ErrorBoundary on_error callback raised",
                        exc_info=cb_exc,
                    )
            logging.getLogger("streamtree.render").exception("ErrorBoundary")
            render_element(el.fallback, slot=f"{slot}.eb_f")
        return

    if isinstance(el, Portal):
        return

    if isinstance(el, PortalMount):
        from streamtree.portals import take_portal_children

        for i, ch in enumerate(take_portal_children(el.slot)):
            render_element(ch, slot=f"{slot}.pm{i}")
        return

    if isinstance(el, SplitView):
        cols = st.columns([el.narrow_ratio, 1.0 - el.narrow_ratio])
        with cols[0]:
            render_element(el.narrow, slot=f"{slot}.sv0")
        with cols[1]:
            render_element(el.main, slot=f"{slot}.sv1")
        return

    if isinstance(el, Routes):
        # sync_route picks the active route name; resolve child by name, then default subtree.
        active = sync_route(el.default, param=el.query_param)
        by_name = dict(el.routes)
        child = by_name.get(active) or by_name[el.default]
        with push_segment("routes"):
            render_element(child, slot=slot)
        return

    if isinstance(el, Text):
        st.write(el.body)
        return

    if isinstance(el, Title):
        st.title(el.text)
        return

    if isinstance(el, Subheader):
        st.subheader(el.text)
        return

    if isinstance(el, Markdown):
        st.markdown(el.body, unsafe_allow_html=el.unsafe_allow_html)
        return

    if isinstance(el, Divider):
        if hasattr(st, "divider"):
            st.divider()
        else:
            st.markdown("---")
        return

    if isinstance(el, Button):
        if el.submit:
            clicked = st.form_submit_button(el.label, disabled=el.disabled, help=el.help or "")
        else:
            clicked = st.button(
                el.label, disabled=el.disabled, help=el.help or "", key=_widget_key(el, "btn", slot)
            )
        if clicked and el.on_click is not None:
            el.on_click()
        return

    if isinstance(el, TextInput):
        _render_text_input(el, slot)
        return

    if isinstance(el, NumberInput):
        _render_number_input(el, slot)
        return

    if isinstance(el, PageLink):
        kw: dict[str, Any] = {
            "page": el.page,
            "label": el.label,
            "disabled": el.disabled,
        }
        if el.icon is not None:
            kw["icon"] = el.icon
        if el.help is not None:
            kw["help"] = el.help
        if el.use_container_width is not None:
            kw["use_container_width"] = el.use_container_width
        st.page_link(**kw)
        return

    if isinstance(el, Selectbox):
        _render_selectbox(el, slot)
        return

    if isinstance(el, Checkbox):
        _render_checkbox(el, slot)
        return

    if isinstance(el, DataFrame):
        kw: dict[str, Any] = {}
        if el.width is not None:
            kw["width"] = el.width
        if el.height is not None:
            kw["height"] = el.height
        st.dataframe(el.data, **kw)
        return

    if isinstance(el, _datagrid_type()):
        from streamtree.tables import DataGrid, render_datagrid

        render_datagrid(cast(DataGrid, el), widget_key=_widget_key(el, "datagrid", slot))
        return

    if isinstance(el, _chart_type()):
        from streamtree.charts import Chart, render_chart

        render_chart(cast(Chart, el), widget_key=_widget_key(el, "chart", slot))
        return

    if isinstance(el, Image):
        kw: dict[str, Any] = {}
        if el.caption is not None:
            kw["caption"] = el.caption
        if el.width is not None:
            kw["width"] = el.width
        if el.use_container_width is not None:
            kw["use_container_width"] = el.use_container_width
        elif el.use_column_width is not None:
            kw["use_column_width"] = el.use_column_width
        st.image(el.image, **kw)
        return

    if isinstance(el, Dialog):
        if not _coerce_open_flag(el.open):
            return
        if hasattr(st, "dialog"):

            @st.dialog(el.title)
            def _dialog_body() -> None:
                for i, ch in enumerate(el.children):
                    render_element(ch, slot=f"{slot}.dlg{i}")

            _dialog_body()
        else:
            st.warning("st.dialog is not available in this Streamlit version.")
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.dlgf{i}")
        return

    if isinstance(el, Popover):
        if hasattr(st, "popover"):
            with st.popover(el.label, disabled=el.disabled):
                for i, ch in enumerate(el.children):
                    render_element(ch, slot=f"{slot}.pop{i}")
        else:
            with st.expander(el.label, expanded=False):
                for i, ch in enumerate(el.children):
                    render_element(ch, slot=f"{slot}.popex{i}")
        return

    if isinstance(el, AuthGate):
        try:
            from streamtree.auth import build_authenticator

            auth = build_authenticator(el.config)
        except ImportError as exc:
            raise ImportError(
                "AuthGate requires streamlit-authenticator. "
                'Install with: pip install "streamtree[auth]"'
            ) from exc
        auth.login(location=el.login_location, key=el.login_key)
        if st.session_state.get("authentication_status"):
            render_element(el.child, slot=f"{slot}.auth_ok")
        return

    if isinstance(el, SocialBadge):
        try:
            from streamlit_extras.badges import badge
        except ImportError as exc:
            raise ImportError(
                'SocialBadge requires streamlit-extras. Install with: pip install "streamtree[ui]"'
            ) from exc
        badge(el.kind, name=el.name, url=el.url)
        return

    if isinstance(el, StyleMetricCards):
        try:
            from streamlit_extras.metric_cards import style_metric_cards
        except ImportError as exc:
            raise ImportError(
                "StyleMetricCards requires streamlit-extras. "
                'Install with: pip install "streamtree[ui]"'
            ) from exc
        style_metric_cards(
            background_color=el.background_color,
            border_size_px=el.border_size_px,
            border_color=el.border_color,
            border_radius_px=el.border_radius_px,
            border_left_color=el.border_left_color,
            box_shadow=el.box_shadow,
        )
        return

    if isinstance(el, ColoredHeader):
        try:
            from streamlit_extras.colored_header import colored_header

            colored_header(el.label, description=el.description, color_name=el.color_name)
        except ImportError as exc:
            raise ImportError(
                "ColoredHeader requires streamlit-extras. "
                'Install with: pip install "streamtree[ui]"'
            ) from exc
        return

    if isinstance(el, VerticalSpaceLines):
        try:
            from streamlit_extras.add_vertical_space import add_vertical_space

            add_vertical_space(el.num_lines)
        except ImportError as exc:
            raise ImportError(
                "VerticalSpaceLines requires streamlit-extras. "
                'Install with: pip install "streamtree[ui]"'
            ) from exc
        return

    if isinstance(el, BottomDock):
        try:
            from streamlit_extras.bottom_container import bottom
        except ImportError as exc:
            raise ImportError(
                'BottomDock requires streamlit-extras. Install with: pip install "streamtree[ui]"'
            ) from exc
        with bottom():
            for i, ch in enumerate(el.children):
                render_element(ch, slot=f"{slot}.bd{i}")
        return

    if isinstance(el, FloatingActionButton):
        try:
            from streamlit_extras.floating_button import floating_button
        except ImportError as exc:
            raise ImportError(
                "FloatingActionButton requires streamlit-extras. "
                'Install with: pip install "streamtree[ui]"'
            ) from exc
        floating_button(
            el.label,
            key=_widget_key(el, "fab", slot),
            help=el.help,
            on_click=el.on_click,
            args=el.on_click_args,
            kwargs=el.on_click_kwargs,
            type=el.button_type,
            icon=el.icon,
            disabled=el.disabled,
        )
        return

    if isinstance(el, Stoggle):
        try:
            from streamlit_extras.stoggle import stoggle
        except ImportError as exc:
            raise ImportError(
                'Stoggle requires streamlit-extras. Install with: pip install "streamtree[ui]"'
            ) from exc
        stoggle(el.summary, el.content)
        return

    if isinstance(el, TaggerRow):
        try:
            from streamlit_extras.tags import tagger_component
        except ImportError as exc:
            raise ImportError(
                'TaggerRow requires streamlit-extras. Install with: pip install "streamtree[ui]"'
            ) from exc
        cn = el.color_name
        if isinstance(cn, tuple):
            cn = list(cn)
        tcn = el.text_color_name
        if isinstance(tcn, tuple):
            tcn = list(tcn)
        tagger_component(el.content, list(el.tags), color_name=cn, text_color_name=tcn)
        return

    if isinstance(el, MentionChip):
        try:
            from streamlit_extras.mention import mention
        except ImportError as exc:
            raise ImportError(
                'MentionChip requires streamlit-extras. Install with: pip install "streamtree[ui]"'
            ) from exc
        mention(el.label, el.url, icon=el.icon, write=True)
        return

    raise TypeError(f"Unsupported element type: {type(el)!r}")


def render(root: Element) -> None:
    """Render a tree with portal gather pre-pass (see ``streamtree.portals``)."""
    from streamtree.portals import portal_render_context

    with portal_render_context(root):
        render_element(root, slot="0")
