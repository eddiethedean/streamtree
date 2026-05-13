"""``DataGrid`` demo (requires ``pip install \"streamtree[tables]\"``)."""

from __future__ import annotations

import pandas as pd

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import DataGrid, Page, Text, VStack


@component
def Demo() -> Element:
    df = pd.DataFrame({"name": ["Ada", "Grace"], "score": [99, 100]})
    return VStack(
        Text("Editable multi-select grid:"), DataGrid(df, editable=True, selection_mode="multiple")
    )


if __name__ == "__main__":
    render(Page(Demo()))
