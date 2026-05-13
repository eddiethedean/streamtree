"""Apache ECharts via ``EChartsChart`` (requires ``pip install \"streamtree[charts]\"``)."""

from __future__ import annotations

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import EChartsChart, Page, VStack


@component
def Demo() -> Element:
    options = {
        "xAxis": {"type": "category", "data": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [120, 200, 150, 80, 70], "type": "bar"}],
        "title": {"text": "ECharts via StreamTree"},
    }
    return VStack(EChartsChart(options, height=360, key="ech1"))


if __name__ == "__main__":
    render(Page(Demo()))
