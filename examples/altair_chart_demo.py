"""Altair ``AltairChart`` demo (requires ``pip install \"streamtree[charts]\"``)."""

from __future__ import annotations

import altair as alt
import pandas as pd

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import AltairChart, Page, VStack


@component
def Demo() -> Element:
    df = pd.DataFrame({"x": ["A", "B", "C"], "y": [3, 1, 2]})
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x=alt.X("x:N", title=None), y=alt.Y("y:Q", title="Value"))
        .properties(height=320, title="Altair via StreamTree")
    )
    return VStack(AltairChart(chart))


if __name__ == "__main__":
    render(Page(Demo()))
