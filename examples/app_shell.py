"""Demo: App shell with page config, optional sidebar, and main body."""

from __future__ import annotations

from streamtree import component, render_app
from streamtree.app import App
from streamtree.elements import Button, Page, Text, VStack
from streamtree.state import state


@component
def SidebarNav() -> object:
    return VStack(Text("Sidebar"), Text("Use App + render_app for set_page_config."))


@component
def Main() -> object:
    n = state(0, key="app_shell_counter")
    return Page(
        Text("Main column"),
        Text(f"Counter: {n()}"),
        Button("+1", on_click=lambda: n.increment(1)),
    )


if __name__ == "__main__":
    render_app(
        App(
            page_title="App shell demo",
            layout="wide",
            sidebar=SidebarNav(),
            body=Main(),
        )
    )
