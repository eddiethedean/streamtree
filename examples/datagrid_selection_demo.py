"""``DataGrid`` with ``on_result`` — react to the AgGrid return value each rerun."""

from __future__ import annotations

from typing import Any

import pandas as pd

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import DataGrid, Page, Text, VStack
from streamtree.state import state


@component
def Demo() -> Element:
    df = pd.DataFrame({"name": ["Ada", "Grace"], "score": [99, 100]})
    summary = state("No AgGrid result yet.", key="ag_summary")

    def on_result(result: Any) -> None:
        # Runs in the same script run as ``AgGrid``; keep this light.
        name = type(result).__name__
        summary.set(f"Last AgGrid return: {name}")

    return VStack(
        Text(summary()),
        DataGrid(df, selection_mode="single", on_result=on_result, key="grid_sel"),
    )


if __name__ == "__main__":
    render(Page(Demo()))
