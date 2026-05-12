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
- **Session-backed state** — `state`, `toggle_state`, `form_state`, `memo`, `cache`
- **Streamlit renderer** — virtual tree → `st.*` on each rerun
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
pip install streamtree==0.2.0
```

**From a clone** (editable, with dev tools):

```bash
git clone https://github.com/streamtree-dev/streamtree.git
cd streamtree
pip install -e ".[dev]"
# or, with uv:
uv sync --extra dev
```

Optional install groups (`tables`, `charts`, `ui`, `auth`, `asyncio`, `cli`) are stub extras today; see [STREAMTREE_DEPENDENCY_STRATEGY.md](docs/STREAMTREE_DEPENDENCY_STRATEGY.md). Combine with e.g. `pip install "streamtree[tables,charts]"` as wrappers land.

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
  routing.py        # query-param route sync + set_route
  forms.py          # Pydantic str-field + JSON validation helpers
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

**Automated (recommended):** configure the **`PYPI_API_TOKEN`** repository secret (PyPI → Account → API tokens, scoped to this project). Push a **version tag** matching `v*` (for example `v0.2.1`); [`.github/workflows/release.yml`](.github/workflows/release.yml) builds with **`uv build`** and publishes via **`pypa/gh-action-pypi-publish`**.

**Manual:** build artifacts with `uv build` (or `python -m build`), then upload the contents of `dist/` to PyPI using **twine** or **uv publish**. Keep `version` in `pyproject.toml`, `streamtree.__version__`, `tests/test_package_meta.py`, and [CHANGELOG.md](CHANGELOG.md) aligned when you cut releases.

---

## License

MIT — see the [`LICENSE`](LICENSE) file.
