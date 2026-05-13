"""Optional charts (Plotly, Altair, ECharts) behind ``pip install \"streamtree[charts]\"``."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import streamlit as st

from streamtree.core.element import Element
from streamtree.echarts_chart import EChartsChart, render_echarts_chart


@dataclass(frozen=True)
class Chart(Element):
    """Render a Plotly figure via ``st.plotly_chart`` (install the ``[charts]`` extra)."""

    figure: Any = None
    use_container_width: bool | None = True

    def __init__(
        self,
        figure: Any,
        *,
        use_container_width: bool | None = True,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "figure", figure)
        object.__setattr__(self, "use_container_width", use_container_width)


def render_chart(el: Chart, *, widget_key: str) -> None:
    try:
        import plotly
    except ImportError as exc:
        raise ImportError(
            'Chart requires plotly. Install with: pip install "streamtree[charts]"'
        ) from exc

    _ = plotly.__version__
    st.plotly_chart(
        el.figure,
        use_container_width=el.use_container_width,
        key=widget_key,
    )


@dataclass(frozen=True)
class AltairChart(Element):
    """Render an Altair chart via ``st.altair_chart`` (install the ``[charts]`` extra)."""

    spec: Any = None
    use_container_width: bool | None = True

    def __init__(
        self,
        spec: Any,
        *,
        use_container_width: bool | None = True,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "spec", spec)
        object.__setattr__(self, "use_container_width", use_container_width)


def render_altair_chart(el: AltairChart, *, widget_key: str) -> None:
    try:
        import altair as alt
    except ImportError as exc:
        raise ImportError(
            'AltairChart requires altair. Install with: pip install "streamtree[charts]"'
        ) from exc

    _ = alt.__version__
    st.altair_chart(
        el.spec,
        use_container_width=el.use_container_width,
        key=widget_key,
    )


__all__ = [
    "AltairChart",
    "Chart",
    "EChartsChart",
    "render_altair_chart",
    "render_chart",
    "render_echarts_chart",
]
