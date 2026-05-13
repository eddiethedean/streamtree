# StreamTree Dependency Strategy

## Purpose

This document outlines recommended dependencies for StreamTree, including which packages should be hard dependencies, which should be optional extras, and why each package is useful.

The goal is to make StreamTree useful out of the box while keeping the core package lightweight, Pythonic, and easy to adopt.

**Product alignment:** The phased product plan and roadmap reference this document—see [PLAN.md](./PLAN.md) and [ROADMAP.md](./ROADMAP.md).

---

# Dependency Philosophy

StreamTree should avoid becoming a heavy framework that installs too much by default.

The best approach is:

1. Keep the base install small
2. Include only dependencies that support the core package identity
3. Use optional extras for heavier or specialized features
4. Wrap third-party packages behind StreamTree APIs when possible
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

The **`[all]`** meta-extra in `pyproject.toml` bundles the pinned **tables**, **charts**, **ui**, **auth**, and **cli** (Typer) dependencies for a one-shot install. Prefer listing only the extras you need for leaner environments.

---

# Recommended Hard Dependencies

These should be installed with the base package.

## streamlit

### Why

Streamlit is the primary render target for StreamTree.

StreamTree exists to provide a composable, typed, declarative component layer on top of Streamlit.

### Usefulness

- Provides the core runtime
- Handles app rendering
- Provides widgets, layouts, session state, caching, and rerun behavior
- Makes StreamTree immediately useful without additional setup

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

streamlit-extras provides many useful Streamlit extensions and utilities that can make StreamTree more powerful immediately.

It can help StreamTree offer richer components without building every small utility from scratch.

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

This dependency gives StreamTree a broader component toolbox early, while still keeping the framework Streamlit-native.

### Risk

The package is a grab bag, so StreamTree should not expose all of it directly without curation.

Recommended approach:
- depend on it
- wrap only the most useful pieces
- keep StreamTree’s public API clean

### Recommendation

Optional dependency behind the **`[ui]`** extra (and included in **`[dev]`** / **`[all]`** for contributor or combined installs). Ship **curated wrappers** in **`streamtree.elements`** / renderers; keep **`streamlit-extras`** out of the core **`dependencies`** list—see `pyproject.toml`.

```toml
[project.optional-dependencies]
ui = ["streamlit-extras>=0.4.3"]
```

---

## pydantic

### Why

Pydantic is central to StreamTree’s typed Python identity.

StreamTree can use Pydantic for:
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

Pydantic helps differentiate StreamTree from a simple Streamlit utility package.

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

StreamTree should lean heavily into modern Python typing.

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

If StreamTree targets only very new Python versions, this can become optional or unnecessary.

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
- aligning with StreamTree’s **`streamtree.asyncio`** surface (see [PLAN.md](./PLAN.md#async-model-first-class-data-plane))

### Strategic value

Keeps the **default** `streamtree` install free of extra threading/async infrastructure while giving data apps a **supported** path for async orchestration.

### Recommendation

Optional dependency under **`async`**, wrapped entirely behind **`streamtree.asyncio`**. Application code should not depend on vendor imports as the primary API.

**As of 0.3.0:** `streamtree.asyncio` ships in the **default** install with a **stdlib** `submit` / `TaskHandle` implementation (daemon threads + `st.session_state` boxes). The **`asyncio`** optional extra in `pyproject.toml` remains an empty stub reserved for a future backend (for example asynclit) without changing import paths.

**As of 0.5.0:** workers may call **`set_task_progress(key=..., value=...)`** (same `key` as **`submit`**) and the UI thread may read **`TaskHandle.progress()`**; updates use the same per-task lock as status/result/error (see module docstring in `streamtree.asyncio`).

```toml
[project.optional-dependencies]
async = [
    "asynclit",
]
```

*(Exact package pin TBD; alternatives may be evaluated as long as they match poll-on-rerun semantics.)*

---

## CLI extra (`streamtree[cli]`)

```bash
pip install "streamtree[cli]"
```

### Typer

**Why:** A small **Typer**-based **`streamtree`** console entrypoint ships in **0.4.0** (`streamtree run`, `streamtree doctor`); **`streamtree init`** in **0.6.0**; **`init --with-pages`** in **0.8.0** scaffolds a multipage sidebar shell. Typer is **not** a core dependency so `pip install streamtree` stays lean.

**Recommendation:** Optional extra **`[cli]`** plus **`[project.scripts]`** `streamtree = "streamtree.cli:main"`. The **`[runner]`** extra remains an **empty metadata stub** (stdlib `streamtree.helpers.runner` ships in the default wheel); **`[pages]`** remains reserved for future pinned multipage deps while **`streamtree.helpers.pages`** (stdlib) ships in the default install as of **0.5.0**—see [ROADMAP.md](./ROADMAP.md).

```toml
[project.optional-dependencies]
cli = ["typer>=0.12.3"]
runner = []
pages = []
```

### Multipage helpers (`streamtree.helpers.pages`)

**As of 0.5.0:** **`streamtree.helpers.pages`** ships in the **default** wheel (stdlib + pathlib). It exposes **`discover_pages`**, **`list_page_entries`**, **`pages_dir_next_to`**, and **`PageEntry`** so apps can align StreamTree trees with Streamlit’s `pages/` layout (labels, sort keys, and paths for **`PageLink`**). **As of 0.8.0:** **`page_links`** builds **`PageLink`** rows from discovery output, and **`streamtree init --with-pages`** wires **`SidebarNav`** + **`page_links`** in generated **`app.py`**. **As of 0.9.0:** **`iter_page_entries`**, **`prefetch_page_sources`**, **`group_page_entries_by_order_prefix`**, **`page_links_sidebar_sections`**, and **`multipage_sidebar_nav`** support sectioned sidebars and optional source **`compile()`** checks without importing page modules—see **`docs/PERFORMANCE.md`** and **`docs/PHASE2_PORTALS_AND_PREFETCH.md`**. The **`[pages]`** extra remains **empty** until optional third-party multipage dependencies are pinned—see [ROADMAP.md](./ROADMAP.md).

### Exploration helpers (`streamtree.helpers.explore`)

**As of 0.10.0:** **`column_summary`** runs on lists of row dicts without pandas. **`dataframe_profile`** targets pandas **`DataFrame`** objects and is documented for environments that already install pandas (**`[tables]`** / **`[dev]`**), matching the optional data stack described under [Tables Extra](#tables-extra-shipped-in-080).

### Enterprise hooks (`streamtree.enterprise`)

**As of 0.10.0:** **`streamtree.enterprise`** ships in the default wheel (stdlib only): **`EventSink`** / **`emit_event`** via **`app_context`**, **`tenant_id`**, and **`redact_secrets`**. No logging or observability vendor is pinned; applications provide concrete sink types.

---

# Tables Extra (shipped in 0.8.0)

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

### StreamTree integration (shipped)

**`DataGrid`** (optional **`[tables]`**) maps to **streamlit-aggrid** when the extra is installed; see **`streamtree.tables`** and **`examples/datagrid_demo.py`**.

Earlier design sketch (still valid at a high level):

```python
DataGrid(
    users,
    selectable=True,
    editable=True,
    on_select=select_user,
)
```

Under the hood, this uses streamlit-aggrid when installed.

**pandas:** ``streamtree.tables`` coerces inputs with **pandas** (``DataFrame`` / tabular data). The **`[tables]`** extra pins **pandas** alongside **streamlit-aggrid** so installs stay reproducible if upstream packages relax their transitive pandas requirement.

### Strategic Value

This is one of the most important optional dependencies for serious business apps.

Many internal tools are table-heavy. A strong table component makes StreamTree far more useful.

### Recommendation

Optional dependency under `tables`.

```toml
[project.optional-dependencies]
tables = [
    "streamlit-aggrid>=0.3.0",
    "pandas>=2.0.0",
]
```

---

# Charts Extra (Plotly + Altair + ECharts shipped in 0.10.0)

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

### StreamTree integration (shipped)

**`Chart`** (optional **`[charts]`**) accepts a Plotly figure and renders via **`st.plotly_chart`**; see **`streamtree.charts`** and **`examples/chart_demo.py`**.

**`AltairChart`** (optional **`[charts]`**, **0.10.0+**) accepts an Altair chart object and renders via **`st.altair_chart`**; see **`streamtree.charts`** and **`examples/altair_chart_demo.py`**.

**`EChartsChart`** (optional **`[charts]`**, **0.10.0+**) accepts an ECharts **options** dict and renders via **`streamlit_echarts.st_echarts`**; see **`examples/echarts_demo.py`**. The **`[charts]`** extra pins **streamlit-echarts** alongside **plotly** and **altair**.

### Recommendation

Optional dependencies under `charts`:

```toml
charts = [
    "plotly>=5.18.0",
    "altair>=5.0.0",
    "streamlit-echarts>=0.4.0",
]
```

---

## streamlit-echarts (shipped)

**0.10.0:** **`EChartsChart`** wraps **`streamlit_echarts.st_echarts`** with an ECharts **options** dict; the **`[charts]`** extra pins **streamlit-echarts** with **plotly** and **altair** (see **`pyproject.toml`**). Forward-looking ideas (gauge/treemap-specific wrappers) may ship as additional elements later.

---

## altair (shipped)

**0.10.0:** **`AltairChart`** wraps **`st.altair_chart`**; the **`[charts]`** extra pins **altair** with **plotly** and **streamlit-echarts** (see **`pyproject.toml`**).

---

# UI Extra

```bash
pip install streamtree[ui]
```

**Shipped wrappers (0.6+):** **`streamlit-extras`** behind **`[ui]`** — see **`streamtree.elements.ui_extra`** and the README “Optional UI extras” list. Subsections below (**streamlit-shadcn-ui**, **extra-streamlit-components**) are **forward-looking** integration sketches, not the current PyPI pins.

## streamlit-shadcn-ui

### Why

streamlit-shadcn-ui provides modern UI components inspired by shadcn/ui.

This could make StreamTree apps look more polished without requiring custom frontend work.

### Usefulness

Useful for:
- cards
- buttons
- badges
- tabs
- alerts
- modern app components
- polished internal tools

### StreamTree Integration Ideas

StreamTree should not expose this dependency directly everywhere.

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

Cookies and routing-related utilities could be very useful for StreamTree’s longer-term app framework direction.

### Risk

Some features may overlap with StreamTree’s own planned abstractions.

Recommended approach:
- use selectively
- wrap behind StreamTree APIs
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

streamlit-authenticator can provide useful authentication functionality for early versions of StreamTree.

### Usefulness

Useful for:
- username/password login
- protected pages
- simple internal app authentication
- session-based user tracking

### StreamTree integration (shipped)

Use **`AuthGate`** with credentials from **`streamtree.auth.build_authenticator`**
(see **`examples/auth_demo.py`**). The **`[auth]`** extra pins **`streamlit-authenticator`**.
**Extension points:** wrap **`AuthGate`** in your own **`@component`** shells, merge
extra keys into the authenticator config dict, or gate **`Routes`** children with
conditional trees—there is **no** separate pluggable **`AuthProvider`** protocol in the
library today; third-party OIDC/SAML stacks remain **bring-your-own** behind your
components and session state.

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

Testing should be a first-class part of StreamTree.

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

**CI:** GitHub Actions runs **`ty check src`** as the canonical static type check (see `.github/workflows/ci.yml`). **mypy** stays in the **`dev`** extra for optional local validation and IDE integration.

### Why

StreamTree should care deeply about typing.

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
    "ty",
    "mypy",
]
```

---

# Suggested pyproject.toml Structure

**Canonical source:** the repository’s **`pyproject.toml`** (pins and extras change there first). The skeleton below matches the **0.10.0** dependency tiers; omit version bounds when drafting locally.

```toml
[project]
name = "streamtree"
dependencies = [
    "streamlit>=1.33.0",
    "pydantic>=2.4.0",
    "typing-extensions>=4.8.0",
]

[project.optional-dependencies]
tables = ["streamlit-aggrid>=0.3.0", "pandas>=2.0.0"]
charts = ["plotly>=5.18.0", "altair>=5.0.0", "streamlit-echarts>=0.4.0"]
ui = ["streamlit-extras>=0.4.3"]
auth = ["streamlit-authenticator>=0.3.3"]
cli = ["typer>=0.12.3"]
asyncio = []
async = []
pages = []
runner = []
all = [
    "streamlit-aggrid>=0.3.0",
    "pandas>=2.0.0",
    "plotly>=5.18.0",
    "altair>=5.0.0",
    "streamlit-echarts>=0.4.0",
    "streamlit-extras>=0.4.3",
    "streamlit-authenticator>=0.3.3",
    "typer>=0.12.3",
]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-xdist>=3.5.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
    "ty>=0.0.30",
    "typer>=0.12.3",
    "streamlit-authenticator>=0.3.3",
    "streamlit-extras>=0.4.3",
    "streamlit-aggrid>=0.3.0",
    "pandas>=2.0.0",
    "plotly>=5.18.0",
    "altair>=5.0.0",
    "streamlit-echarts>=0.4.0",
]
```

Illustrative expansions (alternate UI kits, async vendor loops) appear in the sections below; they are **not** all pinned in the default manifest.

---

# Recommended Public API Strategy

StreamTree should avoid forcing users to learn the APIs of every dependency.

Instead, StreamTree should provide clean wrappers.

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

Users should be able to stay inside the StreamTree mental model.

---

# Dependency Ranking

## Best hard dependencies

1. **streamlit**
2. **pydantic**
3. **typing-extensions**

## Best optional dependencies (pinned in `pyproject.toml` as of 0.10.0)

1. **streamlit-aggrid** — **`[tables]`**
2. **plotly** — **`[charts]`**
3. **altair** — **`[charts]`**
4. **streamlit-echarts** — **`[charts]`**
5. **streamlit-extras** — **`[ui]`**
6. **streamlit-authenticator** — **`[auth]`**
7. **typer** — **`[cli]`**

## Exploratory / design-note dependencies

Not pinned in the default manifest; sections below discuss if/when to adopt **streamlit-shadcn-ui**, **extra-streamlit-components**, **asynclit**, etc.

---

# Final recommendation

The **authoritative** dependency list is **`pyproject.toml`**. As of **0.10.0**:

- **Core:** `streamlit`, `pydantic`, `typing-extensions`.
- **Extras:** `tables` (streamlit-aggrid + pandas), `charts` (plotly + altair + streamlit-echarts), `ui` (streamlit-extras), `auth` (streamlit-authenticator), `cli` (typer); **`[all]`** bundles those five.
- **`[asyncio]`** / **`[async]`**, **`[pages]`**, **`[runner]`** remain empty metadata slots unless future pins are added.

```toml
[project]
dependencies = [
    "streamlit>=1.33.0",
    "pydantic>=2.4.0",
    "typing-extensions>=4.8.0",
]

[project.optional-dependencies]
tables = ["streamlit-aggrid>=0.3.0", "pandas>=2.0.0"]
charts = ["plotly>=5.18.0", "altair>=5.0.0", "streamlit-echarts>=0.4.0"]
ui = ["streamlit-extras>=0.4.3"]
auth = ["streamlit-authenticator>=0.3.3"]
cli = ["typer>=0.12.3"]
all = [
    "streamlit-aggrid>=0.3.0",
    "pandas>=2.0.0",
    "plotly>=5.18.0",
    "altair>=5.0.0",
    "streamlit-echarts>=0.4.0",
    "streamlit-extras>=0.4.3",
    "streamlit-authenticator>=0.3.3",
    "typer>=0.12.3",
]
```

The guiding principle should be:

> StreamTree should feel batteries-included, but not dependency-bloated.
