"""CRUD helpers: URL id + save-intent counter (Phase 3).

Run: ``streamlit run examples/crud_automation_demo.py``

Uses :mod:`streamtree.crud` alongside normal ``state`` for row data. See ``docs/PHASE3_CRUD.md``.
"""

from __future__ import annotations

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.crud import save_intent_counter, selected_id_from_query
from streamtree.elements import Button, Page, Text, TextInput, VStack
from streamtree.routing import set_query_value
from streamtree.state import state


@component
def CrudAutomationDemo() -> Element:
    qid = selected_id_from_query(param="id", default="1")
    name = state("Alpha", key="crud_auto_name")
    save_count, bump_save = save_intent_counter(key="crud_auto_save")

    def pick(id_str: str, nm: str) -> None:
        set_query_value(id_str, param="id")
        name.set(nm)

    return Page(
        VStack(
            Text("## CRUD automation helpers"),
            Text(f"Query id: {qid!r} — bump save intent: {save_count()}"),
            Button("Pick id=1 / Alpha", on_click=lambda: pick("1", "Alpha")),
            Button("Pick id=2 / Beta", on_click=lambda: pick("2", "Beta")),
            TextInput("Name", value=name),
            Button("Simulate save click", on_click=bump_save),
        )
    )


if __name__ == "__main__":
    render(Page(CrudAutomationDemo()))
