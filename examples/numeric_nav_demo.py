"""Numeric ``NumberInput`` grid from Pydantic fields plus a ``PageLink`` example."""

from __future__ import annotations

from pydantic import BaseModel

from streamtree import component
from streamtree.app import App
from streamtree.core.component import render_app
from streamtree.elements import Page, PageLink, Text, VStack
from streamtree.forms import bind_numeric_fields, number_inputs


class LineItem(BaseModel):
    quantity: int = 1
    unit_price: float = 0.0


@component
def MiniForm() -> object:
    bindings = bind_numeric_fields(LineItem, key_prefix="line_item")
    return VStack(
        Text("Adjust values (bound to session state via ``bind_numeric_fields``)."),
        *number_inputs(
            LineItem,
            bindings=bindings,
            field_labels={"quantity": "Quantity", "unit_price": "Unit price"},
        ),
        PageLink(
            "Open About demo page",
            page="pages/1_About_demo.py",
        ),
    )


if __name__ == "__main__":
    render_app(
        App(
            page_title="Numeric + navigation",
            initial_sidebar_state="expanded",
            body=Page(VStack(Text("StreamTree 0.4 forms + PageLink"), MiniForm())),
        )
    )
