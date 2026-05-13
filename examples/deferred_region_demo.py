"""Deferred region via :class:`DeferredFragment` (``st.fragment`` when available).

Run: ``streamlit run examples/deferred_region_demo.py``

On Streamlit builds with ``st.fragment``, children render inside a fragment for
lower scheduling priority; otherwise they render inline like a normal subtree.
"""

from __future__ import annotations

from streamtree import component, render
from streamtree.core.element import Element
from streamtree.elements import DeferredFragment, Page, Text, VStack


@component
def DeferredRegionDemo() -> Element:
    heavy = tuple(Text(f"Row {i}") for i in range(12))
    return Page(
        VStack(
            Text("## DeferredFragment demo"),
            Text("Heavy block below is wrapped for fragment scheduling when supported."),
            DeferredFragment(*heavy),
        )
    )


if __name__ == "__main__":
    render(Page(DeferredRegionDemo()))
