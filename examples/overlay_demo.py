"""Demo: Dialog and Popover overlays (Streamlit 1.33+)."""

from __future__ import annotations

from streamtree import component, render_app
from streamtree.app import App
from streamtree.elements import Button, Dialog, Page, Popover, Text, VStack
from streamtree.state import toggle_state


@component
def Main() -> object:
    show = toggle_state(key="dlg_open", initial=False)
    return Page(
        VStack(
            Text("Open the dialog or popover below."),
            Button("Open dialog", on_click=lambda: show.set(True)),
            Dialog("Example", Text("Dialog body"), open=show),
            Popover("Details", Text("Popover body")),
        )
    )


if __name__ == "__main__":
    render_app(App(page_title="Overlay demo", body=Main()))
