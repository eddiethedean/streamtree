"""Background task demo: ``streamtree.asyncio.submit`` + poll ``status`` / ``result``.

For rerun-polled **progress** from the worker (0.5+), use ``set_task_progress(key=..., value=...)``
with the same ``key`` as ``submit``, and read ``TaskHandle.progress()`` on the main thread.
"""

from __future__ import annotations

import time

from streamtree import component, render
from streamtree.asyncio import submit
from streamtree.elements import Markdown, Page, Text, VStack


@component
def AsyncDemo() -> object:
    h = submit(lambda: time.sleep(0.3) or 42, key="demo_slow_job")
    status = h.status()
    if status == "done":
        return VStack(Text(f"Result: {h.result()}"), Markdown("_Task finished._"))
    if status == "error":
        return Markdown(h.error() or "error")
    return VStack(Text(f"Status: {status}"), Markdown("Rerun to poll until **done**."))


if __name__ == "__main__":
    render(Page(AsyncDemo()))
