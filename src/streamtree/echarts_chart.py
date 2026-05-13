"""Apache ECharts via ``streamlit-echarts`` (``pip install \"streamtree[charts]\"``)."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, cast

from streamtree.core.element import Element


def _st_echarts_call(**kwargs: Any) -> None:
    """Delegate to ``streamlit_echarts.st_echarts`` (patch in unit tests)."""
    try:
        from streamlit_echarts import st_echarts
    except ImportError as exc:
        raise ImportError(
            'EChartsChart requires streamlit-echarts. Install with: pip install "streamtree[charts]"'
        ) from exc

    st_echarts(
        **kwargs
    )  # pragma: no cover — exercised in apps; unit tests patch ``_st_echarts_call``.


@dataclass(frozen=True)
class EChartsChart(Element):
    """Render an ECharts option dict via ``streamlit_echarts.st_echarts`` (install ``[charts]``)."""

    options: Any = None
    height: str | int | None = None

    def __init__(
        self,
        options: Mapping[str, Any] | dict[str, Any],
        *,
        height: str | int | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "options", options)
        object.__setattr__(self, "height", height)


def render_echarts_chart(el: EChartsChart, *, widget_key: str) -> None:
    mapping = cast(Mapping[str, Any], el.options)
    opts = dict(mapping.items())
    if el.height is None:
        height_str = "300px"
    elif isinstance(el.height, int):
        height_str = f"{el.height}px"
    else:
        height_str = el.height

    _st_echarts_call(options=opts, height=height_str, key=widget_key)


__all__ = ["EChartsChart", "render_echarts_chart"]
