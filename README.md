# StreamTree

[![PyPI version](https://img.shields.io/pypi/v/streamtree)](https://pypi.org/project/streamtree/)
[![Python versions](https://img.shields.io/pypi/pyversions/streamtree)](https://pypi.org/project/streamtree/)
[![Docs](https://readthedocs.org/projects/streamtree/badge/?version=stable)](https://streamtree.readthedocs.io/en/stable/)
[![License](https://img.shields.io/pypi/l/streamtree)](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE)
[![CI](https://github.com/eddiethedean/streamtree/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/eddiethedean/streamtree/actions/workflows/ci.yml?query=branch%3Amain)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

**Declarative, typed composition for [Streamlit](https://streamlit.io/).** Build UI as Python data (`@component` functions return element trees); the renderer maps them to `st.*` on each rerun. No separate frontend build.

**Documentation (primary):** **[streamtree.readthedocs.io](https://streamtree.readthedocs.io/en/stable/)** — getting started, recipes, full example source, guides, API reference, and changelog.

## At a glance

| Without StreamTree | With StreamTree |
|--------------------|-----------------|
| Long imperative scripts | `@component` + layouts/widgets as a **tree** |
| Ad hoc `session_state` keys | `state()` scoped to the **render path** |
| Hard to test structure | `streamtree.testing.render_to_tree()` and **`summarize_tree_kinds()`** |

**Includes:** layouts (`Page`, `VStack`, `Form`, `Routes`, …), optional **`[tables]`** / **`[charts]`** / **`[ui]`** / **`[auth]`**, **`streamtree.asyncio`** task helpers, multipage discovery in **`streamtree.helpers.pages`**, optional **`[cli]`** (`streamtree run`, `doctor`, `init`, `tree`, …). Details, version notes, and extras matrix live in the docs.

## Requirements

Python **3.10+**, **Streamlit ≥ 1.33**, **Pydantic v2** (see `pyproject.toml`).

## Install

```bash
pip install streamtree
pip install "streamtree[cli]"    # Typer + streamtree run / doctor / init / tree
# Optional: [tables] [charts] [ui] [auth] — see Dependency strategy on RTD
```

From a clone (contributors):

```bash
git clone https://github.com/streamtree-dev/streamtree.git
cd streamtree
uv sync --extra dev
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

```bash
streamlit run examples/counter.py
# with [cli]:  streamtree run examples/counter.py
```

More patterns (interop with raw `st.*`, `App` / theme, async, routing, multipage, CRUD) are in the **[recipes](https://streamtree.readthedocs.io/en/stable/recipes/)** and **[examples](https://streamtree.readthedocs.io/en/stable/EXAMPLES/)** sections on Read the Docs.

## Documentation map

| Start here | Read the Docs |
|------------|----------------|
| Install & mental model | [Getting started](https://streamtree.readthedocs.io/en/stable/getting-started/) |
| How-to cookbook | [Recipes](https://streamtree.readthedocs.io/en/stable/recipes/) |
| Every `examples/*.py` inlined | [Examples (full source)](https://streamtree.readthedocs.io/en/stable/EXAMPLES/) |
| Testing & `AppTest` | [Testing & debugging](https://streamtree.readthedocs.io/en/stable/TESTING_AND_DEBUG/) |
| Plan, roadmap, deps, performance, phases | [Guides](https://streamtree.readthedocs.io/en/stable/PLAN/) (use the site nav: *Design & roadmap* / *Operations*) |
| Release history | [Changelog](https://streamtree.readthedocs.io/en/stable/CHANGELOG/) |

Design files remain in `docs/` in the repo; the site above is the supported reading path for **stable** releases.

## Contributing

```bash
uv sync --extra dev
uv run ruff format --check .
uv run ruff check src tests
uv run ty check src
uv run pytest
uv run python -m mkdocs build --strict
uv build
```

Same checks with **pip**: `pip install -e ".[dev]"`, then the same `ruff`, `ty`, `pytest`, `mkdocs build --strict`, and `uv build` (or `python -m build`). **Coverage** is enforced at 100% on `src/streamtree` (see `pyproject.toml`).

## Releases

Before tagging **`v*.*.*`**: align **`pyproject.toml`** version, **`CHANGELOG.md`**, and package metadata (see **`tests/test_package_meta.py`**). CI and the [release workflow](https://github.com/eddiethedean/streamtree/blob/main/.github/workflows/release.yml) run lint, typecheck, tests, MkDocs, and **`uv build`**; publishing needs a valid **PyPI** token or trusted publishing setup (details in workflow comments and PyPI docs).

## Limits (Streamlit)

No stable cross-rerun APIs for arbitrary widget focus or DOM control. Prefer **`session_state`**, **query params** (`streamtree.routing`, …), **`st.rerun`**, and **`key=`** discipline. **`Portal` / `PortalMount`** move subtrees within a script; they do not replace Streamlit’s execution model. See **[Portals & prefetch](https://streamtree.readthedocs.io/en/stable/PHASE2_PORTALS_AND_PREFETCH/)** on RTD.

## License

MIT — [LICENSE](https://github.com/streamtree-dev/streamtree/blob/main/LICENSE).
