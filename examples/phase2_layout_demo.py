"""Phase 2 layout demo: SplitView, portals, and forms_layout (run with ``streamlit run``)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from streamtree import component, render
from streamtree.elements import (
    BottomDock,
    Button,
    FloatingActionButton,
    Markdown,
    Page,
    Portal,
    PortalMount,
    SplitView,
    Text,
    VStack,
)
from streamtree.forms import bind_numeric_fields, bind_str_fields
from streamtree.forms_layout import build_model_from_bindings, model_field_grid


class Profile(BaseModel):
    handle: str = Field(min_length=1)
    score: int


@component
def Demo() -> Page:
    sb = bind_str_fields(Profile, key_prefix="p2demo")
    nb = bind_numeric_fields(Profile, key_prefix="p2demo")
    grid = model_field_grid(Profile, (("handle", "score"),), str_bindings=sb, numeric_bindings=nb)

    def save() -> None:
        try:
            build_model_from_bindings(Profile, str_bindings=sb, numeric_bindings=nb)
        except Exception as exc:  # pragma: no cover - demo only
            sb["handle"].set(f"error: {exc}")

    return Page(
        VStack(
            Markdown("## SplitView + Portal + BottomDock + FAB"),
            SplitView(
                narrow=VStack(Text("Narrow strip"), PortalMount(slot="aside")),
                main=VStack(
                    Text("Main column"),
                    grid,
                    Button("Validate", on_click=save),
                    Portal(slot="aside", child=Text("Content for narrow slot")),
                ),
            ),
            PortalMount(slot="footer"),
            Portal(slot="footer", child=Markdown("_Footer via portal_")),
            BottomDock(Text("Pinned bottom area (needs streamlit-extras + st._bottom)")),
            FloatingActionButton("FAB", key="p2fab"),
        )
    )


if __name__ == "__main__":
    render(Demo())
