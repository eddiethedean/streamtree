"""@component decorator and public render entrypoint."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from streamtree.core.context import render_context
from streamtree.core.element import ComponentCall, Element
from streamtree.renderers.streamlit import render_element as _render_streamlit

P = ParamSpec("P")
R = TypeVar("R", bound=Element)


def component(fn: Callable[P, R]) -> Callable[P, ComponentCall]:
    """Mark a function as a Streamtree component.

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
