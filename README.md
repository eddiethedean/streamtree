# StreamTree

[![PyPI version](https://img.shields.io/pypi/v/streamtree)](https://pypi.org/project/streamtree/)
[![Python versions](https://img.shields.io/pypi/pyversions/streamtree)](https://pypi.org/project/streamtree/)
[![License](https://img.shields.io/pypi/l/streamtree)](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/eddiethedean/streamtree/ci.yml?branch=main&label=CI)](https://github.com/eddiethedean/streamtree/actions/workflows/ci.yml?query=branch%3Amain)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

Declarative, typed composition for [Streamlit](https://streamlit.io/). StreamTree adds components, layout primitives, scoped session state, and test-friendly tree rendering while keeping Streamlit’s execution model and widgets. No JavaScript or separate frontend build is required.

## Overview

| Traditional scripts | With StreamTree |
|---------------------|-----------------|
| Layout and widgets mixed in one long file | `@component` functions return an **element tree** |
| Many ad hoc `st.session_state` keys | `state()` and helpers scoped to the render path |
| Structure is hard to inspect or snapshot | `streamtree.testing.render_to_tree()` for tests and docs |

StreamTree is an **architecture layer** for Streamlit, not a React-style web framework.

## Capabilities

- **Components and elements** — `@component`, `render` / `render_app`, layouts (`Page`, `Card`, `Grid`, `VStack`, `Form`, `Tabs`, `Sidebar`, `Routes`, `ErrorBoundary`, and more), and widget wrappers.
- **App shell (0.3+)** — `App` with a guarded `st.set_page_config`, plus optional sidebar and main composition via `render_app`.
- **Theming (0.3+)** — `Theme`, `ThemeRoot`, `theme()`, `theme_css()`, and `app_context.provider(theme=...)`.
- **Background work (0.3+)** — `streamtree.asyncio.submit` and `TaskHandle` for stdlib-thread jobs you poll across reruns.
- **Forms (0.3+)** — Pydantic-oriented helpers: `bind_str_fields` / `str_text_inputs`, plus **`bind_numeric_fields` / `number_inputs`** (0.4+) for `int` / `float` fields (optional `int | None` / `float | None` use model defaults or `None` for an empty number input).
- **CLI (0.4+)** — Optional **`streamtree[cli]`**: `streamtree run` delegates to Streamlit; `streamtree doctor` prints versions (see [examples/streamtree_run_demo.md](examples/streamtree_run_demo.md)).
- **State** — `state`, `toggle_state`, `form_state`, `memo`, `cache`.
- **Routing and context** — Query-param routing (`streamtree.routing`), `ErrorBoundary`, `streamtree.forms` utilities, and `app_context.provider` / `lookup` for shared values.
- **Interop** — Inside `@component`, your function body runs during render; you may call `st.*` (columns, metrics, charts, third-party components) and still return an element tree, or `fragment()` when the subtree is fully imperative.
- **Quality** — Pydantic v2 in the default install, typing-first APIs, and `render_to_tree` for structural tests.

Optional extras (`tables`, `charts`, `ui`, `auth`, `asyncio`, `async`, `pages`, `runner`) are mostly stubs for future wrappers; **`[cli]`** adds **Typer** and the **`streamtree`** console script (`run`, `doctor`). See [Dependency strategy](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md). The `streamtree.asyncio` module and **`streamtree.helpers.runner`** ship in the default package.

## Requirements

Python **3.10+**, with **Streamlit ≥ 1.30** (for `st.page_link` used by `PageLink`), **Pydantic v2**, and **typing-extensions** (see `pyproject.toml`).

## Installation

```bash
pip install streamtree==0.4.1
pip install "streamtree[cli]"   # Typer + ``streamtree run`` / ``streamtree doctor``
```

From a clone, with dev dependencies:

```bash
git clone https://github.com/streamtree-dev/streamtree.git
cd streamtree
uv sync --extra dev
# or: pip install -e ".[dev]"
```

## Quick start

```python
from streamtree import component, render
from streamtree.elements import Button, Card, Page, Text
from streamtree.state import state


@component
def Counter():
    count = state(0)
    return Card(
        Text(f"Count: {count()}"),
        Button("Increment", on_click=lambda: count.increment(1)),
        Button("Reset", on_click=lambda: count.set(0)),
    )


if __name__ == "__main__":
    render(Page(Counter()))
```

Run examples from the repository root:

```bash
streamlit run examples/counter.py
streamlit run examples/routed_app.py
streamlit run examples/app_shell.py
streamlit run examples/async_bg.py
streamlit run examples/model_form.py
streamlit run examples/numeric_nav_demo.py
# With Typer installed (``pip install "streamtree[cli]"``):
streamtree run examples/counter.py
```

## Using Streamlit inside components

The `@component` body runs on every rerun in the same process as `streamlit`. You can call `st.columns`, `st.metric`, plotting APIs, or `components.v1` before returning elements. Use **stable `key=`** arguments on imperative widgets when Streamlit requires them. When a subtree is drawn entirely with `st.*`, return `fragment()`.

```python
import streamlit as st

from streamtree import component, fragment, render
from streamtree.elements import Button, Markdown, Page, TextInput, VStack
from streamtree.state import state


@component
def DashboardHeader():
    band, meta = st.columns([3, 1])
    with band:
        st.title("Operations")
    with meta:
        st.metric("Queue depth", 12, delta=-2)

    notes = state("", key="header_notes")
    return VStack(
        Markdown("**Notes** (StreamTree `TextInput`):"),
        TextInput("Session notes", value=notes),
        Button("Clear notes", on_click=lambda: notes.set("")),
    )


@component
def MetricsStrip():
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            st.metric(f"M{i + 1}", 100 + i * 7, delta=i - 1)
    return fragment()


if __name__ == "__main__":
    render(Page(DashboardHeader(), MetricsStrip()))
```

## App shell, theme, and background tasks

`App` plus `render_app()` centralize page configuration. Combine `ThemeRoot` with `provider(theme=Theme(...))` for CSS variables, and use `streamtree.asyncio.submit` for non-blocking work you observe via `TaskHandle.status` on reruns.

```python
from streamtree import asyncio, component, render_app
from streamtree.app import App
from streamtree.app_context import provider
from streamtree.elements import Page, Text, ThemeRoot, VStack
from streamtree.theme import Theme


@component
def Body():
    handle = asyncio.submit(lambda: 7, key="demo_job")
    return VStack(
        ThemeRoot(),
        Text(f"status={handle.status()} result={handle.result()}"),
    )


if __name__ == "__main__":
    with provider(theme=Theme(primary_color="#0068c9")):
        render_app(App(page_title="Demo", body=Body()))
```

## Patterns

**Grid of components**

```python
from streamtree.elements import Grid

Grid(UserCard(user1), UserCard(user2), columns=2)
```

**Bound text input**

```python
from streamtree.elements import TextInput
from streamtree.state import state

search = state("")
TextInput(label="Search", value=search)
```

## Documentation

| Resource | Description |
|----------|-------------|
| [Plan](https://github.com/streamtree-dev/streamtree/blob/main/docs/PLAN.md) | Vision, architecture, risks |
| [Roadmap](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md) | Phased delivery |
| [Dependency strategy](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md) | Dependencies and optional extras |
| [CHANGELOG](https://github.com/streamtree-dev/streamtree/blob/main/CHANGELOG.md) | Release history |

## Contributing

Install dev tools, then run lint, type check, and tests (mirrors CI on Python 3.10–3.12):

```bash
uv sync --extra dev
uv run ruff format .
uv run ruff check src tests
uv run ty check src
uv run pytest
```

Equivalent with **pip**: `pip install -e ".[dev]"`, then `ruff`, `ty check src`, and `pytest` as above.

## Releases

**Automated:** Add a **`PYPI_API_TOKEN`** secret to the repository. When `main` is green, push a tag of the form **`v0.4.1`**. The [release workflow](https://github.com/streamtree-dev/streamtree/blob/main/.github/workflows/release.yml) runs lint, type check, pytest (including coverage), builds with `uv build`, and publishes to PyPI.

**Manual:** `uv build` (or `python -m build`), then upload `dist/` with **twine** or **`uv publish`**. Keep `pyproject.toml`, `streamtree.__version__`, `tests/test_package_meta.py`, and `CHANGELOG.md` in sync when cutting a release.

## License

MIT. See [LICENSE](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE).
