"""Streamlit backend: maps the virtual element tree to ``st`` calls."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, cast

import streamlit as st

from streamtree.core.context import current_context, push_segment
from streamtree.core.element import ComponentCall, Element, Fragment
from streamtree.elements.layout import (
    Card,
    Columns,
    ErrorBoundary,
    Expander,
    Form,
    Grid,
    HStack,
    Page,
    Routes,
    Sidebar,
    Spacer,
    Tabs,
    VStack,
)
from streamtree.elements.widgets import (
    Button,
    Checkbox,
    DataFrame,
    Divider,
    Image,
    Markdown,
    NumberInput,
    Selectbox,
    Subheader,
    Text,
    TextInput,
    Title,
)
from streamtree.routing import sync_route
from streamtree.state import FormState, StateVar, ToggleState
from streamtree.theme import ThemeRoot, theme_css

__all__ = ["render_element"]


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
        kwargs["value"] = 0
    st.number_input(**kwargs)


def _render_selectbox(el: Selectbox, slot: str) -> None:
    opts = list(el.options)
    kwargs: dict[str, Any] = {
        "label": el.label,
        "options": opts,
        "disabled": el.disabled,
    }
    if el.format_func is not None:
        kwargs["format_func"] = el.format_func

    idx = el.index
    if isinstance(idx, StateVar):
        idx_sv = cast(StateVar[int], idx)
        wk = _widget_key(el, "selectbox", slot)
        i = int(idx_sv())
        kwargs["index"] = min(max(i, 0), max(len(opts) - 1, 0))
        kwargs["key"] = wk
        out = st.selectbox(**kwargs)
        new_i = opts.index(out) if out in opts else kwargs["index"]
        if new_i != i:
            idx_sv.set(new_i)
        return

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
        if len(weights) != len(el.children):
            weights = [1.0] * len(el.children)
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
                el.on_error(exc)
            logging.getLogger("streamtree.render").exception("ErrorBoundary")
            render_element(el.fallback, slot=f"{slot}.eb_f")
        return

    if isinstance(el, Routes):
        active = sync_route(el.default, param=el.query_param)
        by_name = dict(el.routes)
        child = by_name.get(active) or by_name.get(el.default)
        if child is None:
            child = el.routes[0][1]
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

    if isinstance(el, Image):
        kw: dict[str, Any] = {}
        if el.caption is not None:
            kw["caption"] = el.caption
        if el.width is not None:
            kw["width"] = el.width
        if el.use_column_width is not None:
            # Streamlit prefers use_container_width; keep legacy mapping.
            kw["use_column_width"] = el.use_column_width
        st.image(el.image, **kw)
        return

    raise TypeError(f"Unsupported element type: {type(el)!r}")
