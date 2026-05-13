# StreamTree

[![PyPI version](https://img.shields.io/pypi/v/streamtree)](https://pypi.org/project/streamtree/)
[![Python versions](https://img.shields.io/pypi/pyversions/streamtree)](https://pypi.org/project/streamtree/)
[![License](https://img.shields.io/pypi/l/streamtree)](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/streamtree-dev/streamtree/ci.yml?branch=main&label=CI)](https://github.com/streamtree-dev/streamtree/actions/workflows/ci.yml?query=branch%3Amain)
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

- **Components and elements** — `@component`, `render` / `render_app`, layouts (`Page`, `Card`, `Grid`, `VStack`, `Form`, `Tabs`, `Sidebar`, `Routes`, `ErrorBoundary`, **`Dialog`**, **`Popover`**, and more), and widget wrappers.
- **App shell (0.3+)** — `App` with a guarded `st.set_page_config`, plus optional sidebar and main composition via `render_app`.
- **Theming (0.3+)** — `Theme`, `ThemeRoot`, `theme()`, `theme_css()`, and `app_context.provider(theme=...)`.
- **Background work (0.3+)** — `streamtree.asyncio.submit` / **`submit_many`** and `TaskHandle` for stdlib-thread jobs you poll across reruns; **`set_task_progress` / `TaskHandle.progress()`** (0.5+); **0.7+** cooperative cancel via **`TaskHandle.cancel()`**, **`is_task_cancel_requested`**, and **`complete_cancelled`**; **0.8.0+** **`dismiss_task`** clears terminal slots before reusing a ``key`` (see module docstring in `streamtree.asyncio`).
- **Multipage helpers (0.5+)** — **`streamtree.helpers.pages`** (`discover_pages`, **`page_links`** for **`PageLink`** rows, `PageLink`-friendly paths) for Streamlit’s `pages/` layout; ships in the default install (the **`[pages]`** extra remains reserved for future pinned deps). **`streamtree init --with-pages`** (0.8.0+) scaffolds a sidebar wired to **`discover_pages`** + **`page_links`**.
- **Forms (0.3+)** — Pydantic-oriented helpers: `bind_str_fields` / `str_text_inputs`, plus **`bind_numeric_fields` / `number_inputs`** (0.4+) for `int` / `float` fields (optional `int | None` / `float | None` use model defaults or `None` for an empty number input).
- **CLI (0.4+)** — Optional **`streamtree[cli]`**: **`streamtree run`** delegates to Streamlit; **`streamtree doctor`** prints versions; **`streamtree init`** (0.6+) scaffolds **`app.py`** and optional **`pages/`** (see [examples/streamtree_run_demo.md](examples/streamtree_run_demo.md)).
- **State** — `state`, `toggle_state`, `form_state`, `memo`, `cache`.
- **Routing and context** — Query-param routing (`streamtree.routing`), `ErrorBoundary`, `streamtree.forms` utilities, and `app_context.provider` / `lookup` for shared values.
- **Optional auth (0.6+)** — **`pip install "streamtree[auth]"`**: **`AuthGate`** + **`streamtree.auth.build_authenticator`** for **`streamlit-authenticator`** (see [examples/auth_demo.py](examples/auth_demo.py); treat config as trusted secrets).
- **Optional UI extras (0.6+)** — **`pip install "streamtree[ui]"`**: **`ColoredHeader`**, **`VerticalSpaceLines`**, **`SocialBadge`**, **`StyleMetricCards`** (curated **`streamlit-extras`** wrappers).
- **Overlays (0.6+)** — **`Dialog`** / **`Popover`** elements mapped to **`st.dialog`** / **`st.popover`**. On older Streamlit builds without **`st.dialog`**, **`Dialog`** shows a warning and renders its children **inline** on the page (not a modal); **`Popover`** falls back to **`st.expander`**.
- **Interop** — Inside `@component`, your function body runs during render; you may call `st.*` (columns, metrics, charts, third-party components) and still return an element tree, or `fragment()` when the subtree is fully imperative.
- **Data toolkit (0.8+)** — **`pip install "streamtree[tables]"`**: **`DataGrid`** (streamlit-aggrid); **`pip install "streamtree[charts]"`**: **`Chart`** (Plotly via **`st.plotly_chart`**); **`streamtree.loading.match_task`** for declarative loading / ready / error subtrees from **`TaskHandle`**; **`routing.sync_query_value`** / **`set_query_value`** for URL-backed filter strings. See [docs/PERFORMANCE.md](docs/PERFORMANCE.md).
- **Quality** — Pydantic v2 in the default install, typing-first APIs, and `render_to_tree` for structural tests.

Optional extras: **`[tables]`** pins **`streamlit-aggrid`**; **`[charts]`** pins **`plotly`**. **`[ui]`** and **`[auth]`** pin **`streamlit-extras`** and **`streamlit-authenticator`** (0.6+). **`[cli]`** adds **Typer** and the **`streamtree`** console script (`run`, `doctor`, `init`). **`[asyncio]`** / **`[async]`**, **`[pages]`**, and **`[runner]`** remain metadata-oriented. See [Dependency strategy](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md). The `streamtree.asyncio` module and **`streamtree.helpers`** ( **`pages`**, **`runner`**, **`scaffold`** ) ship in the default install; **`import streamtree`** exposes **`streamtree.helpers`** on the root package.

## Requirements

Python **3.10+**, with **Streamlit ≥ 1.33** (for **`st.dialog`** / **`st.popover`** overlays and the current test matrix), **Pydantic v2**, and **typing-extensions** (see `pyproject.toml`). **`PageLink`** continues to require Streamlit’s multipage APIs from the **1.30+** line; the floor is **1.33** for the whole package as of **0.6.0+**.

## Installation

```bash
pip install streamtree==0.8.0
pip install "streamtree[cli]"   # Typer + ``streamtree run`` / ``doctor`` / ``init``
pip install "streamtree[auth]"  # streamlit-authenticator
pip install "streamtree[ui]"    # streamlit-extras wrappers
pip install "streamtree[tables]"  # streamlit-aggrid + ``DataGrid``
pip install "streamtree[charts]"  # plotly + ``Chart``
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
streamlit run examples/pages_helpers_demo.py
streamlit run examples/overlay_demo.py
streamlit run examples/auth_demo.py
streamlit run examples/datagrid_demo.py
streamlit run examples/chart_demo.py
streamlit run examples/async_loader_demo.py
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

`App` plus `render_app()` centralize page configuration. Combine `ThemeRoot` with `provider(theme=Theme(...))` for CSS variables, and use `streamtree.asyncio.submit` for non-blocking work you observe via `TaskHandle.status` (and optionally **`TaskHandle.progress()`**) on reruns. From inside the worker, call **`streamtree.asyncio.set_task_progress`** with the same **`key`** you passed to **`submit`**.

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
        Text(f"status={handle.status()} progress={handle.progress()!r} result={handle.result()}"),
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

**Multipage discovery (0.5+; `page_links` in 0.8.0)**

Use **`streamtree.helpers.pages.discover_pages(__file__)`** to list scripts under Streamlit’s **`pages/`** folder next to your entry script. Each **`PageEntry`** has **`label`** and **`page`** for **`PageLink`**. Use **`streamtree.helpers.page_links(...)`** to turn discovery rows into **`PageLink`** tuples for **`SidebarNav`** or custom shells. See **`examples/pages_helpers_demo.py`**.

## Documentation

| Resource | Description |
|----------|-------------|
| [Plan](https://github.com/streamtree-dev/streamtree/blob/main/docs/PLAN.md) | Vision, architecture, optional extras, release notes through **0.8.0** |
| [Roadmap](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md) | Phased delivery and release index |
| [Phase 2 tail](https://github.com/streamtree-dev/streamtree/blob/main/docs/PHASE2_TAIL.md) | Grooming after **0.6.0** (navigation, asyncio, forms) |
| [Dependency strategy](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md) | Optional extras, **default-install** helpers (`runner`, `pages`), and CI typing notes |
| [Performance](https://github.com/streamtree-dev/streamtree/blob/main/docs/PERFORMANCE.md) | Memoization, background work, URL filter params, optional data extras |
| [CHANGELOG](https://github.com/streamtree-dev/streamtree/blob/main/CHANGELOG.md) | Release history (e.g. **0.8.0** data toolkit + Phase 2 follow-ups; **0.7.1** patch) |

## Contributing

Install dev tools, then run lint, type check, and tests (mirrors CI on Python 3.10–3.13):

```bash
uv sync --extra dev
uv run ruff format .           # apply formatting locally
uv run ruff format --check .   # same check CI runs (no file writes)
uv run ruff check src tests
uv run ty check src
uv run pytest
```

Equivalent with **pip**: `pip install -e ".[dev]"`, then `ruff`, `ruff format` / `ruff format --check`, `ty check src`, and `pytest` as above.

## Releases

Before tagging **`v0.8.0`** (or any **`v*.*.*`** release), confirm **`uv build`** succeeds, **`uv run pytest`** passes with coverage, and **`pyproject.toml`**, **`streamtree.__version__`**, **`tests/test_package_meta.py`**, and **`CHANGELOG.md`** all agree on the version.

**Automated:** Add a **`PYPI_API_TOKEN`** secret to the repository. When `main` is green, push a tag of the form **`v0.8.0`**. The [release workflow](https://github.com/streamtree-dev/streamtree/blob/main/.github/workflows/release.yml) runs lint, type check, pytest (including coverage), builds with `uv build`, and publishes to PyPI.

**Manual:** `uv build` (or `python -m build`), then upload `dist/` with **twine** or **`uv publish`**. Keep `pyproject.toml`, `streamtree.__version__`, `tests/test_package_meta.py`, and `CHANGELOG.md` in sync when cutting a release.

## License

MIT. See [LICENSE](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE).
