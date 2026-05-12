# Streamtree Dependency Strategy

## Purpose

This document outlines recommended dependencies for Streamtree, including which packages should be hard dependencies, which should be optional extras, and why each package is useful.

The goal is to make Streamtree useful out of the box while keeping the core package lightweight, Pythonic, and easy to adopt.

**Product alignment:** The phased product plan and roadmap reference this document—see [STREAMTREE_PLAN.md](./STREAMTREE_PLAN.md) and [STREAMTREE_ROADMAP.md](./STREAMTREE_ROADMAP.md).

---

# Dependency Philosophy

Streamtree should avoid becoming a heavy framework that installs too much by default.

The best approach is:

1. Keep the base install small
2. Include only dependencies that support the core package identity
3. Use optional extras for heavier or specialized features
4. Wrap third-party packages behind Streamtree APIs when possible
5. Preserve a simple user experience

Recommended install tiers:

```bash
pip install streamtree
pip install streamtree[tables]
pip install streamtree[charts]
pip install streamtree[ui]
pip install streamtree[auth]
pip install streamtree[async]
pip install streamtree[dev]
pip install streamtree[all]
```

---

# Recommended Hard Dependencies

These should be installed with the base package.

## streamlit

### Why

Streamlit is the primary render target for Streamtree.

Streamtree exists to provide a composable, typed, declarative component layer on top of Streamlit.

### Usefulness

- Provides the core runtime
- Handles app rendering
- Provides widgets, layouts, session state, caching, and rerun behavior
- Makes Streamtree immediately useful without additional setup

### Recommendation

Hard dependency.

```toml
dependencies = [
    "streamlit",
]
```

---

## streamlit-extras

### Why

streamlit-extras provides many useful Streamlit extensions and utilities that can make Streamtree more powerful immediately.

It can help Streamtree offer richer components without building every small utility from scratch.

### Usefulness

Potentially useful for:
- badges
- stylable containers
- grid helpers
- metric cards
- switches
- markdown helpers
- UI conveniences
- small app-enhancement utilities

### Strategic Value

This dependency gives Streamtree a broader component toolbox early, while still keeping the framework Streamlit-native.

### Risk

The package is a grab bag, so Streamtree should not expose all of it directly without curation.

Recommended approach:
- depend on it
- wrap only the most useful pieces
- keep Streamtree’s public API clean

### Recommendation

Hard dependency, but curated behind Streamtree abstractions.

```toml
dependencies = [
    "streamlit-extras",
]
```

---

## pydantic

### Why

Pydantic is central to Streamtree’s typed Python identity.

Streamtree can use Pydantic for:
- typed component props
- typed forms
- schema-based validation
- automatic form generation
- config models
- page parameter validation

### Usefulness

Example:

```python
class UserForm(BaseModel):
    name: str
    email: EmailStr
    role: Literal["admin", "user"]

Form(UserForm, on_submit=create_user)
```

### Strategic Value

Pydantic helps differentiate Streamtree from a simple Streamlit utility package.

It supports the larger vision:

> Python-native UI architecture with typed components and validation.

### Recommendation

Hard dependency.

```toml
dependencies = [
    "pydantic",
]
```

---

## typing-extensions

### Why

Streamtree should lean heavily into modern Python typing.

typing-extensions helps support modern typing features across Python versions.

### Usefulness

Useful for:
- Annotated
- Literal
- Protocol
- TypedDict
- Self
- ParamSpec
- TypeAlias
- NotRequired

### Recommendation

Hard dependency if supporting older Python versions.

If Streamtree targets only very new Python versions, this can become optional or unnecessary.

```toml
dependencies = [
    "typing-extensions",
]
```

---

# Recommended Optional Dependencies

These should be installed through extras.

---

# Async extra

```bash
pip install streamtree[async]
```

## asynclit (or equivalent)

### Why

Streamlit’s main script is **synchronous** and **rerun-driven**. Heavy **async** or **blocking** I/O on that thread hurts responsiveness. Small worker-loop libraries (for example [asynclit](https://github.com/eddiethedean/asynclit)) submit **sync or async** jobs to a **background event loop** and expose **poll-friendly** task handles (`done`, `result`, `error`, `cancel`, optional **progress**) that fit naturally between reruns.

### Usefulness

Useful for:

- parallel API or database fetches before rendering dashboards
- long-running jobs with **progress** without blocking `st` calls
- cooperative **cancellation** when users navigate away
- aligning with Streamtree’s **`streamtree.asyncio`** surface (see [STREAMTREE_PLAN.md](./STREAMTREE_PLAN.md#async-model-first-class-data-plane))

### Strategic value

Keeps the **default** `streamtree` install free of extra threading/async infrastructure while giving data apps a **supported** path for async orchestration.

### Recommendation

Optional dependency under **`async`**, wrapped entirely behind **`streamtree.asyncio`**. Application code should not depend on vendor imports as the primary API.

**As of 0.3.0:** `streamtree.asyncio` ships in the **default** install with a **stdlib** `submit` / `TaskHandle` implementation (daemon threads + `st.session_state` boxes). The **`asyncio`** optional extra in `pyproject.toml` remains an empty stub reserved for a future backend (for example asynclit) without changing import paths.

```toml
[project.optional-dependencies]
async = [
    "asynclit",
]
```

*(Exact package pin TBD; alternatives may be evaluated as long as they match poll-on-rerun semantics.)*

---

# Tables Extra

```bash
pip install streamtree[tables]
```

## streamlit-aggrid

### Why

Streamlit’s built-in dataframe support is useful, but many production apps need richer table behavior.

streamlit-aggrid provides advanced interactive data grids.

### Usefulness

Useful for:
- sortable tables
- filterable tables
- selectable rows
- editable grids
- enterprise-style data views
- CRUD admin interfaces
- dashboard tables

### Streamtree Integration Ideas

Streamtree could expose:

```python
DataGrid(
    users,
    selectable=True,
    editable=True,
    on_select=select_user,
)
```

Under the hood, this could use streamlit-aggrid when installed.

### Strategic Value

This is one of the most important optional dependencies for serious business apps.

Many internal tools are table-heavy. A strong table component makes Streamtree far more useful.

### Recommendation

Optional dependency under `tables`.

```toml
[project.optional-dependencies]
tables = [
    "streamlit-aggrid",
]
```

---

# Charts Extra

```bash
pip install streamtree[charts]
```

## plotly

### Why

Plotly is one of the most common Python charting libraries for interactive dashboards.

### Usefulness

Useful for:
- interactive charts
- dashboard visualizations
- hover tooltips
- filtering
- business intelligence views
- data exploration

### Streamtree Integration Ideas

```python
Chart(fig)
```

or:

```python
LineChart(data, x="date", y="revenue")
```

### Recommendation

Optional dependency under `charts`.

```toml
charts = [
    "plotly",
]
```

---

## streamlit-echarts

### Why

Apache ECharts is a powerful charting system, and streamlit-echarts makes it available in Streamlit.

### Usefulness

Useful for:
- advanced dashboards
- complex interactive charts
- maps
- gauges
- tree charts
- rich visualizations

### Streamtree Integration Ideas

```python
EChart(options)
```

or curated components like:

```python
Gauge(value=72)
Treemap(data)
```

### Recommendation

Optional dependency under `charts`.

```toml
charts = [
    "streamlit-echarts",
]
```

---

## altair

### Why

Altair is declarative and works naturally with Streamlit.

It fits Streamtree’s declarative philosophy well.

### Usefulness

Useful for:
- concise statistical charts
- declarative chart specs
- simple data visualization
- built-in Streamlit compatibility

### Recommendation

Optional dependency under `charts`.

```toml
charts = [
    "altair",
]
```

---

# UI Extra

```bash
pip install streamtree[ui]
```

## streamlit-shadcn-ui

### Why

streamlit-shadcn-ui provides modern UI components inspired by shadcn/ui.

This could make Streamtree apps look more polished without requiring custom frontend work.

### Usefulness

Useful for:
- cards
- buttons
- badges
- tabs
- alerts
- modern app components
- polished internal tools

### Streamtree Integration Ideas

Streamtree should not expose this dependency directly everywhere.

Instead, it could provide higher-level components:

```python
Badge("Admin")
Alert("Saved successfully", variant="success")
ModernCard(...)
```

### Recommendation

Optional dependency under `ui`.

```toml
ui = [
    "streamlit-shadcn-ui",
]
```

---

## extra-streamlit-components

### Why

extra-streamlit-components provides useful components that fill gaps in Streamlit.

### Usefulness

Useful for:
- cookies
- routers
- tab bars
- toggle-style UI
- miscellaneous UI helpers

### Strategic Value

Cookies and routing-related utilities could be very useful for Streamtree’s longer-term app framework direction.

### Risk

Some features may overlap with Streamtree’s own planned abstractions.

Recommended approach:
- use selectively
- wrap behind Streamtree APIs
- avoid exposing dependency-specific concepts directly

### Recommendation

Optional dependency under `ui` or `auth`.

```toml
ui = [
    "extra-streamlit-components",
]
```

---

# Auth Extra

```bash
pip install streamtree[auth]
```

## streamlit-authenticator

### Why

Many Streamlit apps need login and user management.

streamlit-authenticator can provide useful authentication functionality for early versions of Streamtree.

### Usefulness

Useful for:
- username/password login
- protected pages
- simple internal app authentication
- session-based user tracking

### Streamtree Integration Ideas

```python
AuthProvider(
    config=auth_config,
    children=AppShell(...)
)
```

or:

```python
@app.protected_page("/admin")
def admin():
    return AdminDashboard()
```

### Strategic Value

Authentication is a common pain point for production Streamlit apps.

### Risk

Authentication is sensitive and should be designed carefully.

Recommended approach:
- keep as optional
- clearly document limitations
- eventually support pluggable auth providers

### Recommendation

Optional dependency under `auth`.

```toml
auth = [
    "streamlit-authenticator",
    "extra-streamlit-components",
]
```

---

# Dev Extra

```bash
pip install streamtree[dev]
```

## pytest

### Why

Testing should be a first-class part of Streamtree.

### Usefulness

Useful for:
- component tests
- renderer tests
- snapshot tests
- regression tests

### Recommendation

Development dependency.

```toml
dev = [
    "pytest",
]
```

---

## ruff

### Why

Ruff is a fast Python linter and formatter.

### Usefulness

Useful for:
- linting
- formatting
- import sorting
- code quality

### Recommendation

Development dependency.

```toml
dev = [
    "ruff",
]
```

---

## mypy

### Why

Streamtree should care deeply about typing.

mypy helps validate the package’s own type correctness and supports a strong typed API culture.

### Usefulness

Useful for:
- checking public API typing
- catching internal type issues
- improving IDE behavior
- validating generic component patterns

### Recommendation

Development dependency.

```toml
dev = [
    "mypy",
]
```

---

# Suggested pyproject.toml Structure

```toml
[project]
name = "streamtree"
description = "Composable, typed Streamlit applications."
dependencies = [
    "streamlit",
    "streamlit-extras",
    "pydantic",
    "typing-extensions",
]

[project.optional-dependencies]
tables = [
    "streamlit-aggrid",
]

charts = [
    "plotly",
    "streamlit-echarts",
    "altair",
]

ui = [
    "streamlit-shadcn-ui",
    "extra-streamlit-components",
]

auth = [
    "streamlit-authenticator",
    "extra-streamlit-components",
]

async = [
    "asynclit",
]

dev = [
    "pytest",
    "ruff",
    "mypy",
]

all = [
    "streamlit-aggrid",
    "plotly",
    "streamlit-echarts",
    "altair",
    "streamlit-shadcn-ui",
    "extra-streamlit-components",
    "streamlit-authenticator",
    "asynclit",
]
```

---

# Recommended Public API Strategy

Streamtree should avoid forcing users to learn the APIs of every dependency.

Instead, Streamtree should provide clean wrappers.

Preferred:

```python
DataGrid(...)
Badge(...)
Alert(...)
Chart(...)
AuthProvider(...)
# Async orchestration stays under streamtree.asyncio (not direct vendor imports)
```

Avoid:

```python
from st_aggrid import AgGrid
from streamlit_shadcn_ui import ...
from streamlit_extras import ...
import asynclit  # in app code as the primary pattern
```

Users should be able to stay inside the Streamtree mental model.

---

# Dependency Ranking

## Best Hard Dependencies

1. streamlit
2. pydantic
3. streamlit-extras
4. typing-extensions

## Best Optional Dependencies

1. streamlit-aggrid
2. plotly
3. streamlit-echarts
4. streamlit-shadcn-ui
5. extra-streamlit-components
6. streamlit-authenticator
7. altair
8. asynclit (via **`[async]`** and `streamtree.asyncio`)

---

# Final Recommendation

For v0.1, use:

```toml
dependencies = [
    "streamlit",
    "streamlit-extras",
    "pydantic",
    "typing-extensions",
]
```

Then add optional extras:

```toml
[project.optional-dependencies]
tables = ["streamlit-aggrid"]
charts = ["plotly", "streamlit-echarts", "altair"]
ui = ["streamlit-shadcn-ui", "extra-streamlit-components"]
auth = ["streamlit-authenticator", "extra-streamlit-components"]
async = ["asynclit"]
dev = ["pytest", "ruff", "mypy"]
```

This gives Streamtree a useful base install while keeping heavier capabilities opt-in.

The guiding principle should be:

> Streamtree should feel batteries-included, but not dependency-bloated.
