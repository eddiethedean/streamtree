"""Phase 2 composite: ``ErrorBoundary``, ``app_context``, ``Routes``, ``submit_many``.

Run: ``streamlit run examples/phase2_composite_demo.py``

Wraps the tree in :func:`streamtree.app_context.provider` so ``lookup`` works inside
components. ``submit_many`` jobs use stable keys; rerun to poll until both finish.
"""

from __future__ import annotations

from streamtree import component, render
from streamtree.app_context import lookup, provider
from streamtree.asyncio import submit_many
from streamtree.elements import (
    Button,
    ErrorBoundary,
    Markdown,
    Page,
    Routes,
    Text,
    Title,
    VStack,
)
from streamtree.routing import set_route


@component
def Boom() -> object:
    """Raises on purpose so ``ErrorBoundary`` can show its fallback."""
    raise RuntimeError("demo failure")


@component
def ContextBadge() -> object:
    return Text(f"app_label from context: {lookup('app_label', default='?')!r}")


@component
def ParallelStrip() -> object:
    a, b = submit_many((("demo_a", lambda: 1), ("demo_b", lambda: 2)))
    if a.status() == "done" and b.status() == "done":
        return Text(f"submit_many done: {a.result()} + {b.result()} = 3")
    return Text(f"Parallel jobs: {a.status()=!s} {b.status()=!s} (rerun to poll)")


@component
def App() -> object:
    return Page(
        VStack(
            Title("Phase 2 composite"),
            ErrorBoundary(
                child=Boom(),
                fallback=Markdown("**ErrorBoundary** caught a subtree failure."),
            ),
            ContextBadge(),
            Markdown("---"),
            Button("Home", on_click=lambda: set_route("home")),
            Button("Async strip", on_click=lambda: set_route("async")),
            Routes(
                routes=(
                    ("home", Text("Use buttons above to switch ``route`` query param.")),
                    ("async", ParallelStrip()),
                ),
                default="home",
            ),
        )
    )


if __name__ == "__main__":
    with provider(app_label="phase2-composite-demo"):
        render(App())
