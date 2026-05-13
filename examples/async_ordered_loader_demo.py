"""Parallel tasks with stable key order via :func:`submit_many_ordered`.

Run: ``streamlit run examples/async_ordered_loader_demo.py``

``submit_many_ordered`` sorts task keys before calling :func:`streamtree.asyncio.submit_many`,
so :func:`streamtree.loading.match_task_many` ``ready`` tuples align with that order.
"""

from __future__ import annotations

import time

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import Page, Text, VStack
from streamtree.loading import match_task_many, submit_many_ordered


@component
def AsyncOrderedLoaderDemo() -> Element:
    def job_a() -> str:
        time.sleep(0.05)
        return "A"

    def job_b() -> str:
        time.sleep(0.05)
        return "B"

    handles = submit_many_ordered({"z": job_b, "m": job_a})
    body = match_task_many(
        handles,
        loading=VStack(Text("Loading m then z (sorted keys)…")),
        ready=lambda xs: VStack(Text(f"Results (ordered): {xs}")),
        error=VStack(Text("A task failed.")),
    )
    return Page(
        VStack(
            Text("## submit_many_ordered + match_task_many"),
            body,
            Text("Dismiss tasks from your real app before reusing keys; this demo is read-only."),
        )
    )


if __name__ == "__main__":
    render(Page(AsyncOrderedLoaderDemo()))
