"""List Streamlit ``pages/*.py`` entries via ``streamtree.helpers.pages`` (0.5.0+).

Run from the repository root (so ``examples/pages/`` sits next to this file):

    streamlit run examples/pages_helpers_demo.py
"""

from __future__ import annotations

from streamtree import component, render
from streamtree.elements import Markdown, Page, PageLink, Text, VStack
from streamtree.helpers.pages import discover_pages


@component
def Body():
    entries = discover_pages(__file__)
    if not entries:
        return VStack(
            Markdown("Add scripts under **`examples/pages/`** to see `PageLink` targets here."),
        )
    return VStack(
        Markdown("**Pages** discovered next to this script:"),
        *(PageLink(e.label, page=e.page) for e in entries),
    )


if __name__ == "__main__":
    render(Page(Body()))
