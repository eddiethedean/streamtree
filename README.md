# Streamtree

[![PyPI version](https://img.shields.io/pypi/v/streamtree)](https://pypi.org/project/streamtree/)

**Composable, typed Streamlit applications** — a small Python layer that turns UIs into declarative trees instead of long imperative scripts.

Streamtree keeps Streamlit’s execution model and widgets, but adds **components**, **virtual elements**, **scoped session state**, and a path toward **Pydantic-typed** forms and props. No JavaScript is required for the core experience.

---

## Why Streamtree

| Without Streamtree | With Streamtree |
|--------------------|-----------------|
| Layout and widgets interleaved in one script | `@component` functions return a **tree** of elements |
| `st.session_state` keys scattered and stringly | `state()` keys scoped to the render path |
| Hard to snapshot or reason about structure | `streamtree.testing.render_to_tree()` for structure checks |

Streamtree is **not** a React clone, a browser framework, or a JS build step. It is an **architecture layer** for teams who want maintainable Streamlit apps.

---

## Features

- **Python-first** — decorators, plain functions, standard typing
- **Pydantic v2** in the default install for typed models and validation helpers
- **Declarative layouts** — `Page`, `Card`, `Grid`, `VStack`, `Form`, `Tabs`, `Sidebar`, `Routes`, `ErrorBoundary`, …
- **`App` + `render_app`** — one guarded `st.set_page_config` and optional sidebar + main composition
- **Theming** — `Theme`, `ThemeRoot`, `theme()` / `theme_css()` with `app_context.provider(theme=...)`
- **Background tasks** — `streamtree.asyncio.submit` / `TaskHandle` (poll `status` across reruns; stdlib threads)
- **Form builder slice** — `bind_str_fields` / `str_text_inputs` for Pydantic string fields
- **Session-backed state** — `state`, `toggle_state`, `form_state`, `memo`, `cache`
- **Streamlit renderer** — virtual tree → `st.*` on each rerun
- **Raw `st` when you need it** — `@component` bodies run during render, so you can compose `st.columns`, `st.metric`, custom components, then `return` elements or `fragment()` (see **Custom Streamlit inside `@component`** below)
- **Testing helpers** — serialize trees for snapshots (`render_to_tree`)
- **Typed trajectory** — roadmap and dependency strategy center on **Pydantic** and curated optional extras

---

## Requirements

- **Python 3.10+**
- **Streamlit ≥ 1.28**, **Pydantic v2**, and **typing-extensions** (declared in `pyproject.toml`)

---

## Install

**From PyPI** (after you publish this version):

```bash
pip install streamtree==0.3.0
```

**From a clone** (editable, with dev tools):

```bash
git clone https://github.com/streamtree-dev/streamtree.git
cd streamtree
pip install -e ".[dev]"
# or, with uv:
uv sync --extra dev
```

Optional install groups (`tables`, `charts`, `ui`, `auth`, `asyncio`, `cli`) are stub extras today; see [STREAMTREE_DEPENDENCY_STRATEGY.md](docs/STREAMTREE_DEPENDENCY_STRATEGY.md). The **`streamtree.asyncio`** helpers (thread-pool MVP) ship in the **default** install; the **`asyncio`** extra name stays reserved for future optional backends. Combine with e.g. `pip install "streamtree[tables,charts]"` as wrappers land.

---

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

Run the bundled demo from the repo root:

```bash
streamlit run examples/counter.py
streamlit run examples/routed_app.py
streamlit run examples/app_shell.py
streamlit run examples/async_bg.py
streamlit run examples/model_form.py
```

## Custom Streamlit inside `@component`

The body of a `@component` runs **while the tree is being rendered** (each Streamlit rerun), in the same script context as `st.*`. Anything Streamlit exposes—`st.columns`, `st.metric`, `st.plotly_chart`, `st.download_button`, third-party `components.v1`, and so on—you can call **before** you `return` your `Element` tree. Use that when Streamtree does not yet ship a wrapper for a widget, or when the imperative API is clearer.

Return `fragment()` when everything below was drawn with raw `st` calls and you do not need extra virtual nodes. Mix freely: draw with `st`, then return `VStack`, `Markdown`, `Button`, … for the rest of the subtree.

```python
import streamlit as st

from streamtree import component, fragment, render
from streamtree.elements import Button, Markdown, Page, TextInput, VStack
from streamtree.state import state


@component
def DashboardHeader():
    """Build part of the UI with Streamlit primitives, the rest as elements."""
    band, meta = st.columns([3, 1])
    with band:
        st.title("Operations")
    with meta:
        st.metric("Queue depth", 12, delta=-2)

    notes = state("", key="header_notes")

    return VStack(
        Markdown("**Notes** (Streamtree `TextInput` + `state`):"),
        TextInput("Session notes", value=notes),
        Button("Clear notes", on_click=lambda: notes.set("")),
    )


@component
def SparklineStrip():
    """All-imperative strip: no virtual children, so return an empty `fragment`."""
    cols = st.columns(4)
    for i, col in enumerate(cols):
        with col:
            st.metric(f"M{i + 1}", value=100 + i * 7, delta=i - 1)
    return fragment()


if __name__ == "__main__":
    render(
        Page(
            DashboardHeader(),
            SparklineStrip(),
        )
    )
```

Give every **manual** `st` widget a **stable `key=`** when Streamlit requires it (sliders, inputs, duplicated patterns, etc.) so reruns do not collide with other widgets.

---

## App shell, theming, and background tasks (0.3+)

Use **`App`** with **`render_app()`** for `st.set_page_config` once per session and optional **`Sidebar`** + main body composition. Pair **`ThemeRoot`** with **`provider(theme=Theme(...))`** for CSS variables, and **`streamtree.asyncio.submit`** for work that should not block the main script (poll `TaskHandle.status` on each rerun).

```python
from streamtree import asyncio, component, render_app
from streamtree.app import App
from streamtree.app_context import provider
from streamtree.elements import Page, Text, ThemeRoot, VStack
from streamtree.theme import Theme

@component
def Body() -> object:
    h = asyncio.submit(lambda: 7, key="demo_job")
    return VStack(ThemeRoot(), Text(f"job={h.status()} result={h.result()}"))

if __name__ == "__main__":
    with provider(theme=Theme(primary_color="#0068c9")):
        render_app(App(page_title="Demo", body=Body()))
```

---

## Layout and state at a glance

**Grid of components**

```python
from streamtree.elements import Grid

Grid(
    UserCard(user1),
    UserCard(user2),
    columns=2,
)
```

**Bound text input**

```python
from streamtree.elements import TextInput
from streamtree.state import state

search = state("")
TextInput(label="Search", value=search)
```

## Routing, error boundaries, and forms (0.2+)

**Query-param routing** — keep the active page in sync with `st.query_params` (see `streamtree.routing.sync_route` and the `Routes` element).

**Error boundaries** — wrap fragile subtrees: `ErrorBoundary(child=..., fallback=..., on_error=optional)`.

**Pydantic helpers** — `streamtree.forms.str_field_names`, `model_validate_json`, and `format_validation_errors` for small JSON or string-keyed forms.

**App context** — `streamtree.app_context.provider(theme="dark")` / `lookup("theme")` for values you do not want to thread through every `@component` signature.

---

## Project layout

```text
src/streamtree/     # installable package
  app_context.py    # provider / lookup DI bag (contextvars)
  app.py            # App shell + page_config helpers
  routing.py        # query-param route sync + set_route
  forms.py          # Pydantic helpers + str TextInput bindings
  theme.py          # Theme model + ThemeRoot CSS injection
  asyncio/          # submit / TaskHandle (stdlib thread MVP)
  core/             # elements, @component, render, render_context
  elements/         # layouts + widgets
  state/            # session state helpers
  renderers/        # Streamlit backend
  testing/          # tree serialization for tests
docs/               # plan, roadmap, dependency strategy
examples/           # counter.py, routed_app.py
tests/              # pytest
```

---

## Documentation

| Document | Contents |
|----------|----------|
| [STREAMTREE_PLAN.md](docs/STREAMTREE_PLAN.md) | Vision, goals, architecture, risks |
| [STREAMTREE_ROADMAP.md](docs/STREAMTREE_ROADMAP.md) | Phased delivery and dependency alignment |
| [STREAMTREE_DEPENDENCY_STRATEGY.md](docs/STREAMTREE_DEPENDENCY_STRATEGY.md) | Base vs optional deps, extras, wrapper-first API |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Contributing

With **[uv](https://docs.astral.sh/uv/)** (recommended):

```bash
uv sync --extra dev
uv run ruff check src tests
uv run ty check src
uv run pytest
```

With **pip**:

```bash
pip install -e ".[dev]"
ruff check src tests
ty check src
pytest
```

CI runs the same checks on Python 3.10–3.12 (see `.github/workflows/ci.yml`).

### Publishing

**Automated (recommended):** configure the **`PYPI_API_TOKEN`** repository secret (PyPI → Account → API tokens, scoped to this project). After **`main`** is green in CI, push a **version tag** matching `v*` (for example **`v0.2.0`** for this release); [`.github/workflows/release.yml`](.github/workflows/release.yml) runs **ruff**, **ty**, **pytest** (with the same coverage gate as CI), then **`uv build`**, and publishes via **`pypa/gh-action-pypi-publish`**.

**Manual:** build artifacts with `uv build` (or `python -m build`), then upload the contents of `dist/` to PyPI using **twine** or **uv publish**. Keep `version` in `pyproject.toml`, `streamtree.__version__`, `tests/test_package_meta.py`, and [CHANGELOG.md](CHANGELOG.md) aligned when you cut releases.

---

## License

MIT — see the [`LICENSE`](LICENSE) file.
