---
description: StreamTree — declarative composition for Streamlit. Install, learn, browse examples and API reference.
---

# StreamTree

**Declarative, typed composition for [Streamlit](https://streamlit.io/).** Build virtual UI trees with Python, reuse `@component` functions, and let the renderer translate them into Streamlit widgets on every rerun.

!!! warning "Alpha software"

    APIs may evolve between releases. Pin versions in production and read **[Changelog](CHANGELOG.md)** when upgrading.

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Get started__

    ---

    Install, mental model, and next steps in **[Getting started](getting-started.md)**.

-   :material-book-open-variant:{ .lg .middle } __Recipes__

    ---

    Step-by-step patterns: state, forms, routing, async, multipage, CRUD, and more in the **[Recipes cookbook](recipes/README.md)**.

-   :material-file-code-outline:{ .lg .middle } __Examples__

    ---

    Full source for every script under `examples/` on **[Examples (full source)](EXAMPLES.md)**.

-   :material-api:{ .lg .middle } __API reference__

    ---

    Autodoc for testing helpers, asyncio tasks, core context, CLI helpers — see **API reference** in the tab bar.

-   :material-school-outline:{ .lg .middle } __Design guides__

    ---

    Plan, roadmap, dependency strategy, performance, and phase notes under **Guides → Design & roadmap**.

-   :material-bug-outline:{ .lg .middle } __Testing & debugging__

    ---

    **`AppTest`**, tree snapshots, and debug helpers in **[Testing & debugging](TESTING_AND_DEBUG.md)**.

</div>

## Install (quick)

```bash
pip install streamtree
```

Optional extras (`[tables]`, `[charts]`, `[ui]`, `[auth]`, `[cli]`, …) are described in **[Dependency strategy](DEPENDENCY_STRATEGY.md)**.

## Canonical README

The root **[README on GitHub](https://github.com/streamtree-dev/streamtree/blob/main/README.md)** remains the single source for PyPI: full capability matrix, CLI examples, contributing, and badges.
