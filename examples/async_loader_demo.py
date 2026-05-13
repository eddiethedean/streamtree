"""``match_task`` + :func:`streamtree.asyncio.submit` for loading / ready / error subtrees."""

from __future__ import annotations

import time

from streamtree import asyncio, component, render
from streamtree.core.element import Element
from streamtree.elements import Page, Text, VStack
from streamtree.loading import match_task


@component
def LoaderDemo() -> Element:
    def fetch() -> int:
        time.sleep(0.15)
        return 42

    handle = asyncio.submit(fetch, key="loader_demo_value")

    return match_task(
        handle,
        loading=VStack(Text("Loading…")),
        ready=lambda n: VStack(Text(f"Ready: result={n!r}")),
        error=VStack(Text("Something went wrong.")),
        cancelled=VStack(Text("Cancelled.")),
    )


if __name__ == "__main__":
    render(Page(LoaderDemo()))
