"""Plotly ``Chart`` demo (requires ``pip install \"streamtree[charts]\"``)."""

from __future__ import annotations

import plotly.graph_objects as go

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import Chart, Page, VStack


@component
def Demo() -> Element:
    fig = go.Figure(data=go.Bar(x=["A", "B", "C"], y=[3, 1, 2]))
    fig.update_layout(margin=dict(l=8, r=8, t=32, b=8), height=320)
    return VStack(Chart(fig))


if __name__ == "__main__":
    render(Page(Demo()))
