"""Background task demo: ``streamtree.asyncio.submit`` + poll ``status`` / ``result``.

For rerun-polled **progress** from the worker (0.5+), use ``set_task_progress(key=..., value=...)``
with the same ``key`` as ``submit``, and read ``TaskHandle.progress()`` on the main thread.

**0.7+:** use ``submit_many`` for several independent callables, and cooperative cancel
(``TaskHandle.cancel()`` while **running**, then ``is_task_cancel_requested`` /
``complete_cancelled`` inside long workers) — see ``streamtree.asyncio`` module docstring.
"""

from __future__ import annotations

import time

from streamtree import component, render
from streamtree.asyncio import submit, submit_many
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


@component
def ManySmallJobs() -> object:
    a, b = submit_many((("job_a", lambda: 10), ("job_b", lambda: 20)))
    if a.status() == "done" and b.status() == "done":
        return Text(f"submit_many: {a.result()} + {b.result()} = {a.result()!s} + {b.result()!s}")
    return Text(f"Many jobs: {a.status()=!s} {b.status()=!s} (rerun to poll)")


if __name__ == "__main__":
    render(Page(VStack(AsyncDemo(), Markdown("---"), ManySmallJobs())))
