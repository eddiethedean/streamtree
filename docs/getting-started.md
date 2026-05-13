# Getting started

StreamTree is a **declarative UI layer** on top of [Streamlit](https://streamlit.io/): you build a tree of elements (layouts, widgets, your own `@component` functions) and call `render` or `render_app` so the built-in renderer maps them to `st.*` APIs on each rerun.

!!! note "Requirements"

    - **Python** 3.10+
    - **Streamlit** ≥ 1.33 (see `pyproject.toml` in the repo for the current floor)

## Install

```bash
pip install streamtree
```

Optional groups (tables, charts, UI extras, auth, CLI) are documented in **[Dependency strategy](DEPENDENCY_STRATEGY.md)**.

## Minimal mental model

1. **Define** a function that returns an `Element` tree (often with `@component`).
2. **Mount** it with `render(Page(...))` or `render_app(App(...))` under `if __name__ == "__main__":`.
3. **Run** with `streamlit run your_app.py`.

The **[First app & components](recipes/first-app-and-components.md)** recipe walks through the smallest counter-style app and links to `examples/counter.py`.

## Where to go next

| Goal | Page |
|------|------|
| Cookbook patterns | [Recipes overview](recipes/README.md) |
| Every `examples/*.py` file inlined | [Examples (full source)](EXAMPLES.md) |
| Testing & `AppTest` | [Testing & debugging](TESTING_AND_DEBUG.md) |
| Architecture & phases | [Guides → Design & roadmap](PLAN.md) |

## Repository README

Install matrices, capability tables, `streamtree` CLI usage, contributing, and CI badges live in the **canonical [README on GitHub](https://github.com/streamtree-dev/streamtree/blob/main/README.md)** so PyPI and the repo stay in sync.
