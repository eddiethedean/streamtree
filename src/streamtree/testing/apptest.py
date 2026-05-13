"""Thin helpers around Streamlit's :class:`streamlit.testing.v1.AppTest`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., None])


def run_app_function(fn: F, *, timeout: int = 20) -> Any:
    """Build an :class:`~streamlit.testing.v1.AppTest` from ``fn`` and ``.run()`` it once.

    ``fn`` should be a no-argument callable containing a Streamlit script body (typically
    calling :func:`streamtree.core.component.render` or :func:`streamtree.core.component.render_app`).
    Returns the :class:`~streamlit.testing.v1.AppTest` instance after ``run`` completes.
    """
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_function(fn)
    return at.run(timeout=timeout)


__all__ = ["run_app_function"]
