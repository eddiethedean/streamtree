
# Streamtree Plan Document

## Vision

Streamtree is a Python-native component framework for building maintainable, composable, and typed Streamlit applications.

The framework introduces a declarative component architecture inspired by modern UI systems while remaining deeply Pythonic and fully compatible with Streamlit’s execution model.

Core philosophy:
- Python first
- Zero JavaScript required for MVP
- Strong typing
- Declarative composition
- Streamlit-native rendering
- Minimal boilerplate
- Enterprise-friendly architecture
- **Async where it earns its keep** — first-class support for **data and orchestration** (parallel I/O, background work, cancellation), not a replacement for Streamlit’s **sync, rerun-driven** UI thread

---

# Dependencies and packaging

**Canonical detail:** [STREAMTREE_DEPENDENCY_STRATEGY.md](./STREAMTREE_DEPENDENCY_STRATEGY.md) (recommended hard vs optional packages, `pyproject.toml` shape, and risks).

## Philosophy

- Keep the **base install small** and aligned with Streamtree’s identity (composable, typed, Streamlit-native).
- Treat **only** dependencies that support that identity as **hard** dependencies.
- Put **heavier or specialized** stacks behind **optional extras** (`tables`, `charts`, `ui`, `auth`, `dev`, `all`).
- **Wrap** third-party packages behind Streamtree elements and APIs where practical so users stay in one mental model.
- Prefer **batteries-included, not dependency-bloated**: useful defaults without pulling every ecosystem package by default.

## Intended tiers (install)

```text
pip install streamtree
pip install streamtree[tables]
pip install streamtree[charts]
pip install streamtree[ui]
pip install streamtree[auth]
pip install streamtree[async]
pip install streamtree[dev]
pip install streamtree[all]
```

## Hard dependencies (target)

Per the dependency strategy, the base package should standardize on:

| Package | Role |
|---------|------|
| **streamlit** | Primary runtime and render target |
| **pydantic** | Typed props, forms, validation, config models |
| **typing-extensions** | Portable modern typing (when Python version warrants it) |
| **streamlit-extras** | Curated building blocks (badges, metric cards, helpers); **expose only through Streamtree**, not as a re-export surface |

## Optional extras (target)

| Extra | Purpose (summary) |
|-------|-------------------|
| **tables** | Rich grids (e.g. streamlit-aggrid) for sortable/filterable/editable tables |
| **charts** | plotly, streamlit-echarts, altair behind elements like `Chart` / `LineChart` / `EChart` |
| **ui** | Polished components (e.g. streamlit-shadcn-ui, extra-streamlit-components) behind names like `Badge`, `Alert`, `ModernCard` |
| **auth** | streamlit-authenticator (+ shared helpers) behind abstractions like `AuthProvider` / protected routes |
| **async** | Optional background task / poll integration (e.g. worker loop helpers) behind **`streamtree.asyncio`** — see plan async model |
| **dev** | pytest, ruff, mypy for contributors and typed app authors |

## Public API rule

Users should prefer Streamtree primitives (`DataGrid`, `Badge`, `Chart`, `AuthProvider`, …). Avoid documenting patterns that require `from streamlit_extras import …` or similar as the primary workflow; wrappers and clear optional-extra gates are the default story.

---

# Problem Statement

Large Streamlit applications often become difficult to maintain because:
- UI logic is written imperatively
- State handling becomes scattered
- Reusable components are awkward
- Testing is difficult
- Layouts become deeply nested
- Teams lack design-system consistency

Streamtree solves these issues by introducing:
- composable UI components
- centralized state abstractions
- reusable layouts
- render abstraction
- testable component trees

---

# Goals

## Primary Goals

1. Make Streamlit applications maintainable at scale
2. Preserve Streamlit simplicity
3. Create a Pythonic component model
4. Enable reusable UI systems
5. Support strong typing and IDE tooling
6. Eliminate the need for JavaScript in most use cases
7. **First-class async for data and orchestration** — parallel and non-blocking I/O, task lifecycle, and loading/error UX, without fighting Streamlit’s rerun model

## Non-Goals (Initial Versions)

- Replacing Streamlit
- Recreating React exactly
- Building a browser virtual DOM runtime
- Supporting arbitrary frontend frameworks in v1
- An **async-first UI reconciler** or fine-grained concurrent widget tree (Streamlit remains **one synchronous script run per rerun** for the main UI path)

---

# Architecture Overview

## Core Flow

Component -> Virtual Tree -> Renderer -> Streamlit

Users define components as Python functions that return UI elements.

The renderer converts those elements into Streamlit primitives.

## Async model (first-class, data-plane)

Streamtree treats **async** as a **first-class concern for work that must not block the rerun thread** and for **composing long-running or parallel data fetches**, while keeping **element construction and the Streamlit renderer path synchronous** unless and until Streamlit’s own model evolves.

**Principles**

1. **Sync tree, async data** — Components still **return** element trees synchronously on each rerun; async is used to **populate** state or props via **explicit** primitives (loaders, tasks, gathers), not by making every `@component` implicitly `async def`.
2. **Rerun-native completion** — Results land in **`st.session_state`** (or Streamtree state keyed the same way) so the **next** rerun picks up `done` / `error` / `cancelled` / partial progress without blocking `render()`.
3. **Cancellation and stale runs** — Any first-class async API must define what happens when a new rerun supersedes an in-flight request (ignore stale results, cooperative cancel, keyed by request generation).
4. **Progress and errors** — First-class paths for **loading**, **terminal error**, and optional **progress** streams (mirroring “Suspense-shaped” boundaries in the roadmap) without requiring users to wire threads by hand.
5. **Interoperability** — Ecosystem libraries that follow the same **background loop + poll on rerun** pattern (for example [asynclit](https://github.com/eddiethedean/asynclit)) are candidates for an **optional extra** or documented integration, wrapped behind Streamtree names so apps do not depend on vendor imports as their primary API.

**Non-goals for async**

- Replacing Streamlit’s **top-level** script execution model with `asyncio.run()` per page as the default.
- Hiding **race conditions** behind magic; users should see **clear** task identity and state keys.

---

# Core Modules

## streamtree.core

Provides:
- Element base classes
- Component decorator
- Tree construction
- Rendering interfaces

## streamtree.elements

Provides:
- Text
- Button
- Card
- Grid
- Tabs
- Sidebar
- Form
- Input controls

Over time, optional extras add **curated** elements (tables, charts, shadcn-style UI) that delegate to optional dependencies without expanding the default install.

## streamtree.state

Provides:
- state()
- toggle_state()
- form_state()
- session_state()
- memo()
- cache()

Backed internally by st.session_state.

## streamtree.renderers

Provides:
- Streamlit renderer
- Future alternate renderers

## streamtree.testing

Provides:
- render_to_tree()
- snapshot testing
- component assertions

## streamtree.asyncio (planned name)

Provides **first-class async orchestration** for Streamlit apps (exact module path may evolve):

- Task submission and **polling** APIs aligned with rerun semantics (`done`, `result`, `error`, `cancel`)
- Optional **progress** bridging for long async jobs
- **`gather`-style** parallel async/sync work for dashboards
- Session-scoped task registries keyed consistently with render context
- Documentation for **testing** async-augmented trees (mocks, `AppTest`, timing between reruns)

Implementation may wrap a small third-party layer or ship a minimal in-tree runtime; either way the **public** surface stays `streamtree.*`.

---

# Design Principles

## Pythonic APIs

Preferred:

count = state(0)

count.increment()

Avoid:
- tuple-heavy APIs
- hook ordering rules
- JSX syntax

## Declarative Layouts

Preferred:

Grid(
    UserCard(user1),
    UserCard(user2),
    columns=2,
)

Avoid:
- nested with-block pyramids

## Typed Components

Preferred:

@component
def UserCard(user: User):
    ...

Strong IDE support is a core goal.

**Pydantic** (see dependency strategy) is the intended backbone for typed props, form models, and validation—not ad-hoc dicts.

## Async API style

Preferred:

- Explicit **task** or **loader** objects with **poll-on-rerun** semantics tied to `session_state`
- **`gather`-style** composition for parallel independent fetches before building the tree
- Clear **loading / error / cancelled** branches in the returned element tree

Avoid:

- Implicit global asyncio policies that hide which rerun a result belongs to
- Blocking `await` in the middle of `render()` unless Streamlit’s runtime explicitly supports that pattern for your target version

---

# Example API

```python
from streamtree import component, render
from streamtree.elements import Page, Card, Text, Button
from streamtree.state import state

@component
def Counter():
    count = state(0)

    return Card(
        Text(f"Count: {count()}"),
        Button(
            "Increment",
            on_click=count.increment,
        ),
    )

render(Page(Counter()))
```

---

# Technical Risks

## Streamlit Rerun Model

The framework must work with Streamlit’s rerun behavior rather than fighting it.

Mitigation:
- deterministic state abstractions
- controlled event dispatch
- predictable component identity

## Component Identity

Lists and dynamic trees require stable keys.

Mitigation:
- explicit key support
- automatic scoped naming

## Async vs Streamlit reruns

Concurrent fetches and background tasks can **race** user input and reruns; stale results can overwrite fresh state if not keyed and generation-scoped.

Mitigation:
- **request / task generation** counters per logical loader
- **documented** cancellation and “stale result discarded” behavior in `streamtree.asyncio` APIs
- integration tests that simulate **multiple rapid reruns** and assert final UI state

---

# Long-Term Opportunities

- FastAPI integration and **native async** request handlers feeding the same virtual-tree abstractions where the renderer allows
- Multi-renderer architecture
- Design systems
- Storybook-style tooling
- Enterprise component libraries
- Typed forms
- Data application tooling
- Authentication layers
- Component marketplaces
- **Streaming and live data** (WebSockets, server-sent style updates) behind optional backends, still bridged through session-safe state

---

# Success Criteria

A successful Streamtree application should:
- feel natural to Python developers
- reduce Streamlit boilerplate
- improve maintainability
- scale to large teams
- require minimal frontend knowledge
- handle **async data and parallel I/O** through first-class, documented primitives without blocking the rerun thread or relying on ad-hoc threading patterns

---

# Related documents

- [STREAMTREE_DEPENDENCY_STRATEGY.md](./STREAMTREE_DEPENDENCY_STRATEGY.md) — hard vs optional dependencies, extras, and wrapper-first API guidance
- [STREAMTREE_ROADMAP.md](./STREAMTREE_ROADMAP.md) — phased delivery, including dependency alignment per phase
