"""In-memory CRUD + ``match_task_many`` / ``submit`` pattern (Phase 3 reference).

Run: ``streamlit run examples/crud_pattern_demo.py``

See ``docs/PHASE3_CRUD.md`` for how this maps to ``DataGrid``, URL filters, and optional extras.
"""

from __future__ import annotations

import time
from typing import Any

from streamtree import asyncio, component, render
from streamtree.core.element import Element
from streamtree.elements import Button, Form, Page, Text, TextInput, VStack
from streamtree.loading import match_task_many
from streamtree.state import state


def _rows() -> list[dict[str, Any]]:
    return [{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}]


@component
def CrudPatternDemo() -> Element:
    rows = state(list(_rows()), key="crud_rows")
    selected_id = state(1, key="crud_sel")
    name_edit = state("Alpha", key="crud_name")

    def sync_refs() -> tuple[int, int]:
        time.sleep(0.08)
        return (1, 2)

    h1 = asyncio.submit(lambda: sync_refs()[0], key="crud_prefetch_a")
    h2 = asyncio.submit(lambda: sync_refs()[1], key="crud_prefetch_b")
    sync_banner = match_task_many(
        (h1, h2),
        loading=VStack(Text("Loading reference data…")),
        ready=lambda _: VStack(Text("Reference checks complete.")),
        error=VStack(Text("Reference load failed.")),
    )

    def select_row(rid: int, current_name: str) -> None:
        selected_id.set(rid)
        name_edit.set(current_name)

    def apply_edit() -> None:
        rid = int(selected_id())
        name = str(name_edit()).strip()
        if not name:
            return
        updated = [{**r, "name": name} if r["id"] == rid else r for r in rows()]
        rows.set(updated)

    def add_row() -> None:
        name = str(name_edit()).strip() or "New"
        nxt = max((r["id"] for r in rows()), default=0) + 1
        rows.set([*rows(), {"id": nxt, "name": name}])
        selected_id.set(nxt)

    row_buttons: list[Element] = []
    for r in rows():
        rid, nm = r["id"], r["name"]
        row_buttons.append(
            Button(
                f"{rid}: {nm}",
                on_click=lambda rid=rid, nm=nm: select_row(rid, nm),
            )
        )

    return VStack(
        Text("## CRUD pattern (in-memory)"),
        sync_banner,
        Text("Select a row, edit the name, then **Apply**."),
        *row_buttons,
        Form(
            TextInput("Name", value=name_edit),
            Button("Apply edit", on_click=apply_edit),
            Button("Add row (uses name field)", on_click=add_row),
            form_key="crud_form",
        ),
    )


if __name__ == "__main__":
    render(Page(CrudPatternDemo()))
