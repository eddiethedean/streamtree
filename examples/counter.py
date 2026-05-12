"""Run with: ``streamlit run examples/counter.py`` from the repo root."""

from __future__ import annotations

from streamtree import component, render
from streamtree.elements import Button, Card, Page, Text
from streamtree.state import state


@component
def Counter():
    count = state(0, key="demo_counter")

    return Card(
        Text(f"Count: {count()}"),
        Button("Increment", on_click=lambda: count.increment(1)),
        Button("Reset", on_click=lambda: count.set(0)),
    )


if __name__ == "__main__":
    render(Page(Counter(), key="page"))
