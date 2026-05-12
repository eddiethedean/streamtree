"""Serialize element trees for snapshots and unit tests."""

from __future__ import annotations

from typing import Any

from streamtree.elements.auth_gate import AuthGate
from streamtree.core.element import ComponentCall, Element, Fragment
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
    Routes,
    Sidebar,
    Spacer,
    Tabs,
    VStack,
)
from streamtree.elements.ui_extra import ColoredHeader, VerticalSpaceLines
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
from streamtree.theme import ThemeRoot

__all__ = ["render_to_tree"]


def _kind(el: Element) -> str:
    return type(el).__name__


def render_to_tree(
    root: Element,
    *,
    expand_components: bool = False,
) -> dict[str, Any]:
    """Convert a virtual element tree into JSON-friendly data.

    By default, :class:`streamtree.core.element.ComponentCall` nodes are not
    executed (no Streamlit context required). Set ``expand_components=True`` to
    expand them; callers must wrap execution in :func:`streamtree.core.context.render_context`
    and have an active Streamlit session (``st.session_state``) when components use ``state()``.
    """
    return _node(root, expand_components=expand_components)


def _node(el: Element, *, expand_components: bool) -> dict[str, Any]:
    if isinstance(el, Fragment):
        return {
            "kind": "Fragment",
            "key": el.key,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, ThemeRoot):
        return {"kind": "ThemeRoot", "key": el.key}

    if isinstance(el, ComponentCall):
        if expand_components:
            from streamtree.core.context import push_segment
            from streamtree.renderers.streamlit import _ensure_component_result

            seg = el.key or getattr(el.fn, "__name__", "component")
            with push_segment(seg):
                inner = el.fn(*el.args, **el.kwargs)
            inner = _ensure_component_result(inner, el.fn)
            return _node(inner, expand_components=expand_components)
        return {
            "kind": "ComponentCall",
            "key": el.key,
            "name": getattr(el.fn, "__name__", "component"),
            "args": _safe_repr(el.args),
            "kwargs": {k: _safe_repr(v) for k, v in el.kwargs.items()},
        }

    if isinstance(el, Dialog):
        return {
            "kind": "Dialog",
            "key": el.key,
            "title": el.title,
            "open_type": type(el.open).__name__,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Popover):
        return {
            "kind": "Popover",
            "key": el.key,
            "label": el.label,
            "disabled": el.disabled,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, (VStack, Page, Card)):
        return {
            "kind": _kind(el),
            "key": el.key,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, HStack):
        return {
            "kind": "HStack",
            "key": el.key,
            "gap": el.gap,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, ErrorBoundary):
        return {
            "kind": "ErrorBoundary",
            "key": el.key,
            "child": _node(el.child, expand_components=expand_components),
            "fallback": _node(el.fallback, expand_components=expand_components),
            "has_on_error": el.on_error is not None,
        }

    if isinstance(el, Routes):
        return {
            "kind": "Routes",
            "key": el.key,
            "default": el.default,
            "query_param": el.query_param,
            "route_names": [n for n, _ in el.routes],
        }

    if isinstance(el, Columns):
        return {
            "kind": "Columns",
            "key": el.key,
            "weights": list(el.weights),
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Grid):
        return {
            "kind": "Grid",
            "key": el.key,
            "columns": el.columns,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Tabs):
        return {
            "kind": "Tabs",
            "key": el.key,
            "tabs": [
                {"title": t, "child": _node(child, expand_components=expand_components)}
                for t, child in el.tabs
            ],
        }

    if isinstance(el, Sidebar):
        return {
            "kind": "Sidebar",
            "key": el.key,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Form):
        return {
            "kind": "Form",
            "key": el.key,
            "form_key": el.form_key,
            "clear_on_submit": el.clear_on_submit,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Expander):
        return {
            "kind": "Expander",
            "key": el.key,
            "label": el.label,
            "expanded": el.expanded,
            "children": [_node(c, expand_components=expand_components) for c in el.children],
        }

    if isinstance(el, Spacer):
        return {"kind": "Spacer", "key": el.key, "height": el.height}

    if isinstance(el, Text):
        return {"kind": "Text", "key": el.key, "body": el.body}
    if isinstance(el, Title):
        return {"kind": "Title", "key": el.key, "text": el.text}
    if isinstance(el, Subheader):
        return {"kind": "Subheader", "key": el.key, "text": el.text}
    if isinstance(el, Markdown):
        return {
            "kind": "Markdown",
            "key": el.key,
            "body": el.body,
            "unsafe_allow_html": el.unsafe_allow_html,
        }
    if isinstance(el, Divider):
        return {"kind": "Divider", "key": el.key}

    if isinstance(el, Button):
        return {
            "kind": "Button",
            "key": el.key,
            "label": el.label,
            "disabled": el.disabled,
            "submit": el.submit,
            "has_on_click": el.on_click is not None,
        }

    if isinstance(el, TextInput):
        return {
            "kind": "TextInput",
            "key": el.key,
            "label": el.label,
            "value_type": type(el.value).__name__ if el.value is not None else None,
        }
    if isinstance(el, NumberInput):
        return {"kind": "NumberInput", "key": el.key, "label": el.label}
    if isinstance(el, PageLink):
        return {
            "kind": "PageLink",
            "key": el.key,
            "label": el.label,
            "page": el.page,
            "disabled": el.disabled,
        }
    if isinstance(el, Selectbox):
        return {
            "kind": "Selectbox",
            "key": el.key,
            "label": el.label,
            "options": list(el.options),
        }
    if isinstance(el, Checkbox):
        return {"kind": "Checkbox", "key": el.key, "label": el.label}
    if isinstance(el, DataFrame):
        return {"kind": "DataFrame", "key": el.key}
    if isinstance(el, Image):
        return {"kind": "Image", "key": el.key}

    if isinstance(el, AuthGate):
        return {
            "kind": "AuthGate",
            "key": el.key,
            "config_keys": sorted(el.config.keys()),
            "child": _node(el.child, expand_components=expand_components),
            "login_location": el.login_location,
        }

    if isinstance(el, ColoredHeader):
        return {
            "kind": "ColoredHeader",
            "key": el.key,
            "label": el.label,
            "description": el.description,
            "color_name": el.color_name,
        }

    if isinstance(el, VerticalSpaceLines):
        return {"kind": "VerticalSpaceLines", "key": el.key, "num_lines": el.num_lines}

    raise TypeError(f"Unsupported element type: {type(el)!r}")


def _safe_repr(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    if isinstance(value, (list, tuple)):
        return [_safe_repr(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _safe_repr(v) for k, v in value.items()}
    if isinstance(value, Element):
        return _node(value, expand_components=False)
    return repr(value)
