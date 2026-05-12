# Streamtree

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
- **Declarative layouts** — `Page`, `Card`, `Grid`, `VStack`, `Form`, `Tabs`, `Sidebar`, …
- **Session-backed state** — `state`, `toggle_state`, `form_state`, `memo`, `cache`
- **Streamlit renderer** — virtual tree → `st.*` on each rerun
- **Testing helpers** — serialize trees for snapshots (`render_to_tree`)
- **Typed trajectory** — roadmap and dependency strategy center on **Pydantic** and curated optional extras

---

## Requirements

- **Python 3.10+**
- **Streamlit ≥ 1.28** (declared in `pyproject.toml`)

---

## Install

**From PyPI** (when published):

```bash
pip install streamtree
```

**From a clone** (editable, with dev tools):

```bash
git clone https://github.com/streamtree-dev/streamtree.git
cd streamtree
pip install -e ".[dev]"
```

Optional install groups (`tables`, `charts`, `ui`, `auth`, `all`) are specified in the [dependency strategy](docs/STREAMTREE_DEPENDENCY_STRATEGY.md) and will appear in `pyproject.toml` as those integrations ship.

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

---

## Project layout

```text
src/streamtree/     # installable package
  core/             # elements, @component, render, context
  elements/         # layouts + widgets
  state/            # session state helpers
  renderers/        # Streamlit backend
  testing/          # tree serialization for tests
docs/               # plan, roadmap, dependency strategy
examples/           # runnable Streamlit examples
tests/              # pytest
```

---

## Documentation

| Document | Contents |
|----------|----------|
| [STREAMTREE_PLAN.md](docs/STREAMTREE_PLAN.md) | Vision, goals, architecture, risks |
| [STREAMTREE_ROADMAP.md](docs/STREAMTREE_ROADMAP.md) | Phased delivery and dependency alignment |
| [STREAMTREE_DEPENDENCY_STRATEGY.md](docs/STREAMTREE_DEPENDENCY_STRATEGY.md) | Base vs optional deps, extras, wrapper-first API |

---

## Contributing

```bash
pip install -e ".[dev]"
ruff check src tests
pytest
```

---

## License

MIT — see `pyproject.toml`.
