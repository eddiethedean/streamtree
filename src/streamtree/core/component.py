"""@component decorator and public render entrypoint."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from streamtree.core.context import render_context
from streamtree.core.element import ComponentCall, Element
from streamtree.renderers.streamlit import render_element as _render_streamlit

if TYPE_CHECKING:
    from streamtree.app import App

P = ParamSpec("P")
R = TypeVar("R", bound=Element)


def component(fn: Callable[P, R]) -> Callable[P, ComponentCall]:
    """Mark a function as a StreamTree component.

    The function body runs when the tree is rendered (each Streamlit rerun),
    not when building the virtual tree from call sites like ``Page(Counter())``.
    """

    @wraps(fn)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> ComponentCall:
        kw = dict(kwargs)
        key = kw.pop("key", None)  # type: ignore[assignment]
        return ComponentCall(fn=fn, args=args, kwargs=kw, key=key)  # type: ignore[arg-type]

    return wrapper  # type: ignore[return-value]


def render(root: Element, *, context_root: str = "app") -> None:
    """Render a virtual element tree using the Streamlit backend."""
    with render_context(context_root):
        _render_streamlit(root)


def render_app(app: App, *, context_root: str = "app") -> None:
    """Render an :class:`streamtree.app.App` shell (page config once, then body/sidebar tree)."""
    from streamtree.app import App as AppShell
    from streamtree.app import app_root_element, apply_page_config

    if not isinstance(app, AppShell):
        raise TypeError(f"render_app expects App, got {type(app)!r}")
    apply_page_config(app)
    with render_context(context_root):
        _render_streamlit(app_root_element(app))
