
# StreamTree Roadmap

This roadmap is aligned with the dependency and packaging approach in [DEPENDENCY_STRATEGY.md](./DEPENDENCY_STRATEGY.md) (base vs optional extras, wrapper-first public API) and with the **async model** in [PLAN.md](./PLAN.md#async-model-first-class-data-plane).

## Progress and release alignment

_Last updated: 2026-05-12._

| Phase | Status | Release notes |
|-------|--------|---------------|
| Phase 0 — Foundation | Mostly complete | Package layout, Streamlit renderer, plan / roadmap / strategy docs. |
| Phase 1 — MVP | In progress | **0.1.0**: core elements, state, `render`, `render_to_tree`. **0.2.0**: adds **Pydantic** + **typing-extensions** and stub extras; `streamlit-extras` and deeper memoization APIs still open. |
| Phase 2 — Application features | In progress | **0.2.0**: routing, `Routes`, `ErrorBoundary`, `app_context`, forms helpers. **0.3.0**: `App` + `render_app`, `theme` / `ThemeRoot`, `streamtree.asyncio` (stdlib thread MVP), `bind_str_fields` / `str_text_inputs`. **Still open for 0.3.1+ / 0.4.0:** richer **App** navigation, **auth**, **portals**, **imperative handles**, **route prefetch**, **`streamlit-extras`** curation, deeper **form builder** / async progress, **optional dedicated helpers** (`[pages]`, `[runner]`; see backlog), **StreamTree–first app create/run** (see [End-to-end app experience](#end-to-end-app-experience-optional-streamlit-cli)). |
| Phase 3+ | Planned | Data toolkit and performance work; timing follows Phase 2 closure. |
| Docs — Read the Docs | Planned | Full **user manual**, **how-to guides**, and **API reference** on **Read the Docs** (versioned **stable** / **latest**); CI doc builds; see [Documentation platform](#documentation-platform-read-the-docs). |

### 0.3.0 (Phase 2 — second tranche, shipped)

- **`streamtree.app`**: `App`, `apply_page_config`, `app_root_element`, and `render_app()` with guarded `st.set_page_config`.
- **`streamtree.theme`**: `Theme` (Pydantic), `theme()` / `theme_css()`, `ThemeRoot` for CSS injection alongside `provider(theme=...)`.
- **`streamtree.asyncio`**: `submit` / `TaskHandle` for daemon-thread work keyed in `st.session_state` (stdlib-only; `[asyncio]` extra remains a documented slot for future backends).
- **`streamtree.forms`**: `bind_str_fields`, `str_text_inputs` for Pydantic string-field `TextInput` grids.
- **Examples:** `examples/app_shell.py`, `examples/async_bg.py`, `examples/model_form.py`.

### 0.2.0 (first Phase 2 tranche, shipped)

- **Dependencies:** Pydantic v2 and typing-extensions in the default install; stub optional extras (`tables`, `charts`, `ui`, `auth`, `asyncio`, `async`, `cli`, `all`). **`[async]`** and **`[asyncio]`** are the same empty stub in `pyproject.toml` (quoted TOML key for the former).
- **Routing + query params:** `streamtree.routing.sync_route`, `set_route`, and the `Routes` layout element; see `examples/routed_app.py`.
- **Error boundaries:** `ErrorBoundary` with fallback subtree, optional `on_error`, and `logging` on the default path.
- **Context / DI (minimal):** `streamtree.app_context` with `provider`, `lookup`, and `current_bag`.
- **Typed forms (slice):** `streamtree.forms` (`str_field_names`, `model_validate_json`, `format_validation_errors`).

### Phase 2 — remaining after 0.3.0 (backlog)

- Richer **App** / **navigation framework** (beyond shell + `Routes` composition)
- **Authentication** abstractions and **`[auth]`** wrappers
- **Portals / layout targets**, **imperative handles**
- **Route-level async prefetch** and optional **progress** surfaces on `streamtree.asyncio`
- **`streamlit-extras`** curation behind StreamTree names
- **Form builder** beyond string `TextInput` grids (numeric fields, layout presets, submit batching)
- **Optional dedicated helpers** (small opt-in modules; empty **`pyproject.toml` extras** reserved first, same pattern as **`[cli]`** / **`[tables]`**):
  - **`[pages]`** + **`streamtree.helpers.pages`** (working name) — bridge Streamlit **multipage** / `pages/` and stable navigation APIs with **`Routes`**, **`sync_route` / `set_route`**, and **`App`**; ship with a documented Streamlit version matrix (no second web server).
  - **`[runner]`** + **`streamtree.helpers.runner`** (working name) — optional **`streamlit run`** orchestration (defaults, workspace-relative entrypoints); evolves toward a **primary `streamtree run` / `serve` story** so authors are not required to invoke the Streamlit CLI. Complements the Typer **`streamtree`** **`[cli]`** surface (`preview`, `doctor`, `tree`, …). **Streamlit remains the execution engine** on this path until multi-renderer hosts (Phase 5) exist.

### End-to-end app experience (optional Streamlit CLI)

**Goal** — Teams can **author and run full StreamTree apps** through a **single documented StreamTree workflow** (scaffold → configure → run) **without needing** the Streamlit CLI, `streamlit run …`, or hand-wired entry scripts **if they prefer not to**.

- **Baseline (always supported)** — Calling **`streamlit run app.py`** (or equivalent) stays valid for transparency, CI, and power users.
- **Streamlined path (planned)** — **`streamtree init`** (or similar) plus **`streamtree run` / `streamtree serve`** (names TBD) under the **`[cli]`** + **`[runner]`** story: resolve the app entry from project metadata or conventions, apply **sane defaults** (host, port, headless flags), and delegate to Streamlit under the hood so **“full app” development and running** feel first-party to StreamTree.
- **Scope boundary** — This is **not** a second web server in Phase 2–4; it is a **developer-experience and packaging layer** on top of Streamlit. **Phase 5** multi-renderer work may add true alternate hosts later; until then, “no Streamlit CLI” means **no obligation to learn Streamlit’s CLI surface**, not removing Streamlit from the stack.
- **Read the Docs** — The **full user manual and guides** for this workflow (and for the rest of StreamTree) are planned on **RTD** under [Documentation platform](#documentation-platform-read-the-docs); README stays a short entry point.

---

# Patterns from React ergonomics (non-VDOM, rerun-native)

StreamTree is **not** React and will **not** ship a browser virtual DOM. The items below borrow **product lessons** from common React-era patterns and adapt them to **Streamlit’s script rerun model**. They are spread across phases; each phase lists concrete work.

1. **Error boundaries** — isolate a subtree’s failures; render fallback UI and capture errors without killing the whole app.
2. **Context / dependency injection** — pass theme, tenant, feature flags, or route-level data deep in the tree without prop drilling (generalizing beyond key-only render context).
3. **Stable list identity and keyed updates** — stronger key/slot semantics for dynamic children (lists of cards, dashboards) so state and identity stay aligned across reruns.
4. **Subtree memoization** — skip rebuilding parts of the virtual tree when inputs are unchanged (e.g. Pydantic props, cached query results), saving CPU each rerun without a DOM reconciler.
5. **Transitions / deferred regions** — treat some UI regions as lower priority under load (chunked rendering, fragments, or documented patterns) so heavy dashboards stay responsive.
6. **Suspense-shaped async boundaries** — unified async data + loading placeholder + error surface for components (not async React; Streamlit-native scheduling).
7. **Imperative handles** — escape hatches where Streamlit allows them: focus, scroll, file triggers, and similar (document limitations; no generic DOM ref model).
8. **Portals / layout targets** — declaratively attach a subtree to another layout region (e.g. sidebar, dialog, toast column) while keeping composition tree-shaped.
9. **Dev-only introspection** — devtools-style visibility into tree, props snapshots, and which `session_state` keys a subtree binds (extends component tree visualization).
10. **Async task orchestration** — submit sync/async work off the blocking rerun path; **poll** completion, errors, cancellation, and optional **progress** via session-scoped handles so each rerun stays fast (implementation may compose ecosystem helpers such as [asynclit](https://github.com/eddiethedean/asynclit) behind `streamtree.*`).

| # | Pattern | Primary phases |
|---|---------|----------------|
| 1 | Error boundaries | 2, 5 |
| 2 | Context / DI | 2, 5 |
| 3 | Keyed lists / identity | 1, 2 |
| 4 | Subtree memoization | 1, 3 |
| 5 | Transitions / deferred regions | 3 |
| 6 | Async / Suspense-shaped boundaries | 1, 2, 3 |
| 7 | Imperative handles | 2 |
| 8 | Portals / layout targets | 2 |
| 9 | Dev introspection | 4 |
| 10 | Async task orchestration | 2, 3, 4, 5 |

---

# Phase 0 — Foundation

## Goals
- Establish package architecture
- Build core rendering concepts
- Validate developer ergonomics
- Lock dependency philosophy: small **hard** set, heavier stacks **opt-in** via extras

## Deliverables
- Element base classes
- Component decorator
- Tree renderer
- Basic Streamlit renderer
- Minimal documentation
- **Pattern philosophy** — short doc tying Phase 0–1 behavior to [Patterns from React ergonomics](#patterns-from-react-ergonomics-non-vdom-rerun-native) (keys, reruns, no VDOM)
- **Async + rerun** — document how async work is **polled across reruns** (never blocking the main Streamlit thread for I/O), stale-run rules, and pointers to the plan’s [async model](./PLAN.md#async-model-first-class-data-plane)
- **`pyproject.toml` aligned with strategy:** documented install tiers (`streamtree`, `[tables]`, `[charts]`, `[ui]`, `[auth]`, `[async]`, `[cli]`, `[dev]`, `[all]`) and rationale (see plan + dependency strategy doc)

---

# Phase 1 — MVP

## Goals
- Build a usable application framework
- Preserve Streamlit simplicity
- Deliver core layout primitives

## Features

### Elements
- Text
- Markdown
- Button
- TextInput
- NumberInput
- SelectBox
- Checkbox
- DataFrame
- Image

### Layouts
- VStack
- HStack
- Grid
- Columns
- Tabs
- Sidebar
- Form
- Card

### State
- state()
- toggle_state()
- form_state()
- session_state()

### Rendering
- render()
- component identity
- key management

### Rerun-native patterns (foundation)
- **Keyed dynamic lists** — document and enforce key/slot conventions for lists and conditional trees (precursor to stronger list identity in later phases)
- **Subtree memoization (initial)** — hooks or primitives to memoize pure virtual-tree fragments on unchanged inputs where MVP scope allows
- **Suspense-shaped loading (documented)** — minimal pattern: branch UI on task/loader state (`loading` / `ready` / `error`) keyed in `session_state`, without blocking `render()`

### Async (MVP scope)
- **Official guidance** — when to use Streamlit built-ins (`st.cache_data`, fragments) vs future **`streamtree.asyncio`** primitives
- **Optional thin helpers** — e.g. session-scoped “submit job + poll dict” helper or a single reference example, if scope allows; otherwise defer to Phase 2–3 with explicit tracking in this roadmap

## Dependency alignment (MVP)
- Ship **core** with the **hard** dependency set from the strategy (`streamlit`, `pydantic`, `typing-extensions`, `streamlit-extras`) once wrappers are ready; until then document any gap vs the strategy doc
- Introduce **Pydantic** for typed component props and early form models where MVP scope allows
- Add **curated** `streamlit-extras`-backed helpers only behind stable StreamTree names (avoid exposing the full grab bag)

## Deliverables
- pip-installable package
- documentation
- examples
- demo applications
- **Base dependencies** per strategy: `streamlit`, `pydantic`, `typing-extensions`, `streamlit-extras` (only **curated** surfaces in `streamtree.*`, not blanket re-exports)
- **Stub or document optional extras** in `pyproject.toml` (`tables`, `charts`, `ui`, `auth`, `async`, `cli`, `all`) even if wrappers land in later phases
- **Optional `[async]` extra (documented)** — reserve name for a future thin integration (e.g. [asynclit](https://github.com/eddiethedean/asynclit)) behind `streamtree.asyncio` without making it part of the default install until APIs stabilize

---

# Phase 2 — Application Features

## Goals
- Support real production applications

### Release notes

What shipped in **0.2.0** and **0.3.0** versus what stays on the **Phase 2** backlog is summarized under [Progress and release alignment](#progress-and-release-alignment).

## Features
- Routing
- Page system
- Query param synchronization
- Typed forms (Pydantic-first models and validation)
- Validation helpers
- Theme system
- Authentication abstractions
- **Error boundaries** — `try`/`except`-style wrappers around subtrees with fallback UI and structured logging
- **Context / DI** — scoped providers for theme, tenant, flags, and route-level data without threading through every component signature
- **Portals / layout targets** — elements or APIs that render a declared subtree into sidebar, dialog, or other supported Streamlit regions while preserving a single composition model
- **Imperative handles** — supported focus, scroll, and widget actions exposed through StreamTree where Streamlit’s API allows; clear docs where not possible
- **Session-scoped async tasks** — **`streamtree.asyncio`** MVP (`submit` / `TaskHandle`, stdlib threads); **progress**, richer cancellation, and **route-level async prefetch** remain on the backlog
- **Route-level async prefetch (optional)** — parallel warm-up when entering a page, with stale-run discard when query params or auth context change

## Optional dependency alignment
- **`[auth]` extra:** `streamlit-authenticator` (+ shared helpers such as `extra-streamlit-components` where needed), wrapped as `AuthProvider`, protected routes, or similar—document limitations and future pluggable providers
- **`[ui]` extra:** use `streamlit-shadcn-ui` / `extra-streamlit-components` only behind StreamTree components (badges, alerts, modern cards, tab bars, cookie/router helpers) to avoid API leakage
- **`[async]` extra (when shipped):** optional backend for background event-loop + poll semantics (e.g. asynclit), exposed only through **`streamtree.asyncio`** — no primary-doc workflow that requires `import asynclit` in app code

## Deliverables
- **App object** (initial): `App` + `render_app` + guarded `set_page_config`; richer navigation framework still planned
- Navigation framework
- **Theme engine** (initial): `Theme`, `theme()`, `ThemeRoot` CSS injection via `app_context`; deeper Streamlit-native theming TBD
- **Form builder** (initial): `bind_str_fields` / `str_text_inputs`; richer field types and layout still planned
- **Resilience and ergonomics** — documented error-boundary usage, context providers, and portal/layout-target patterns in example apps
- **Async example app** — at least one sample using **parallel** async (or threaded) data loads + loading/error branches without blocking the rerun thread

---

# Phase 3 — Data Application Toolkit

## Goals
- Become the best architecture layer for data apps

## Features
- Data tables
- CRUD scaffolding
- Filtering systems
- Query state management
- Dashboard layouts
- Chart wrappers
- **Subtree memoization** — first-class memo of expensive branches (large tables, charts) keyed by props or query fingerprints
- **Transitions / deferred regions** — patterns or primitives for lower-priority regions and chunked work on large dashboards (pair with Streamlit fragments and caching guidance)
- **Suspense-shaped async boundaries** — async data loading with consistent loading and error UI at component boundaries for data-heavy pages
- **`streamtree.asyncio` module** — first release: task submit, **poll** across reruns, cancel, optional **progress**, and **`gather`-style** parallel composition; keys integrated with render context and `session_state`
- **Declarative async loaders** — elements or builder APIs that pair **async/sync jobs** with **ready / loading / error** subtrees (same mental model as pattern 6)

## Optional dependency alignment
- **`[tables]` extra:** `streamlit-aggrid` (or equivalent) behind elements such as `DataGrid` (selectable, editable, filterable rows)
- **`[charts]` extra:** `plotly`, `streamlit-echarts`, `altair` behind elements such as `Chart`, `LineChart`, `EChart`—declarative specs where it matches StreamTree’s model
- **`[async]` extra (when shipped):** optional worker-loop integration (see Phase 2); default docs use **`streamtree.asyncio`** public API only

## Deliverables
- Admin dashboard templates
- Data exploration toolkit
- Enterprise data components
- **Performance playbook** — guidance and APIs for memoized subtrees, deferred regions, and async loading boundaries on realistic datasets
- **`streamtree.asyncio` reference** — full API doc, cancellation semantics, and “stale run” rules for dashboard-scale workloads

---

# Phase 4 — Testing and Tooling

## Goals
- Enable enterprise-scale development workflows
- **Optional StreamTree–first app lifecycle** — `streamtree run` / `serve` (planned) wraps Streamlit so full apps ship without authors touching `streamlit run` unless they want to
- **Read the Docs as the canonical learning surface** — README + repo markdown remain summaries; the **fleshed-out manual and guides** live on RTD (see [Documentation platform](#documentation-platform-read-the-docs))

## Features
- Snapshot testing
- `render_to_tree()` for JSON-style tree snapshots (tests, logs, CI)
- **Component tree visualization** — interactive inspector (expand/collapse, keys, component names) in devtools, a dev sidebar, or the preview server; optional export (e.g. Mermaid/graph) from the same tree walk
- **Dev-only introspection** — props snapshots, component names, and bound `session_state` / StreamTree state keys surfaced in devtools or the preview server (React DevTools–style signal, rerun-native)
- **In-flight async inspection** — surface pending **`streamtree.asyncio`** tasks (status, key, age) next to the component tree in dev mode
- **Typer CLI (`streamtree`)** — optional **`[cli]`** extra: subcommands for **app lifecycle** (e.g. **`run` / `serve`** wrapping `streamlit run` with stable defaults and project-aware entry resolution) and **devtools** (`preview` for the component preview server, **`doctor`** for versions/extras, **`tree`** to dump or export `render_to_tree` JSON/Mermaid, optional **`init`** scaffolding once templates stabilize); keeps the default library install free of CLI dependencies
- Component assertions
- Storybook-style previews
- Devtools
- State inspection

## Optional dependency alignment
- **`[dev]` extra:** `pytest`, `ruff`, `mypy` as the standard contributor and CI toolchain (see dependency strategy)
- **`[cli]` extra (when shipped):** `typer` (and minimal related deps) for the `streamtree` console entry — **not** required for `import streamtree`; **`streamlit run`** remains the documented fallback when the CLI is not installed

## Deliverables
- pytest integration
- Component preview server (isolated runs + **tree view** of the current page)
- Visual regression tooling
- **Introspection deliverables** — devtools or server views that expose props snapshots and state-key bindings alongside the tree inspector
- **Async testing kit** — examples and helpers for **Streamlit AppTest** (or equivalent) with tasks completing between reruns; guidance on mocking `streamtree.asyncio` boundaries
- **Typer CLI deliverable** — `project.scripts` entry for `streamtree`, user-facing command reference (including **run/serve** and **init**), and CI-friendly non-interactive flags where applicable
- **Documentation handoff** — CLI help text and **RTD** cross-links stay aligned with the [Documentation platform](#documentation-platform-read-the-docs) manual and guides

---

# Documentation platform (Read the Docs)

## Goals
- Publish a **versioned, searchable documentation site** on [**Read the Docs**](https://readthedocs.org/) as the **primary home** for learning StreamTree beyond the README and design docs in `docs/`.

## Scope (fully fleshed out over several releases)

### User manual (narrative)
- **Concepts** — rerun execution, virtual trees vs raw `st.*`, `@component`, keys and identity, `render` / `render_app`, `App` shell.
- **Core libraries** — layouts and widgets, `state` / forms / routing / `app_context`, `ErrorBoundary`, `Theme` / `ThemeRoot`, `streamtree.asyncio`, testing with `render_to_tree`.
- **Optional extras** — what each stub extra (`[tables]`, `[charts]`, `[ui]`, `[auth]`, `[cli]`, `[pages]`, `[runner]`, …) is for and when to opt in; matrix vs Streamlit versions where APIs differ.
- **Interop** — documented patterns for mixing Streamlit primitives inside components, performance cautions, and deployment notes (Community Cloud, containers, reverse proxies).

### How-to guides (task-oriented)
- **First full app** — from `pip install` to `App` + sidebar + theme + one background task.
- **Routing** — query params, `Routes`, syncing URLs, error boundaries in real apps.
- **Forms** — Pydantic models, validation UX, `bind_str_fields` / `str_text_inputs` and future builder slices.
- **Async work** — `submit` / `TaskHandle`, polling, cancellation semantics, testing async boundaries.
- **Lifecycle** — once `streamtree run` / `init` exist, end-to-end “create → run → ship” tutorials tied to the [End-to-end app experience](#end-to-end-app-experience-optional-streamlit-cli) roadmap.

### API reference
- **Autogenerated** from Python docstrings (Sphinx **autodoc** or MkDocs **mkdocstrings**—toolchain choice recorded in-repo).
- **Cross-linking** — intersphinx (or equivalent) to **Streamlit**, **Pydantic**, and stdlib where it reduces duplicate prose.
- **Stable URLs** — per-symbol pages suitable for bookmarking from the manual.

### Operations & contributor docs
- **Stable vs latest** — RTD versions aligned with **PyPI** and **git tags**; policy for when `latest` tracks `main`.
- **CI** — doc build on pull requests; **fail on broken references / build warnings** where practical.
- **Contributing** — how to preview docs locally, style guide for prose, and how roadmap items become manual chapters.

## Deliverables
- **RTD project** wired to the GitHub repository (webhooks, maintainers, canonical project slug—e.g. `streamtree` on readthedocs.io, subject to naming availability).
- **Doc site skeleton** — navigation (Manual · Guides · API · release notes on-site or prominent link to `CHANGELOG.md`), search, accessible theme (incl. dark mode if the doc theme supports it), mobile-friendly layouts.
- **MVP publication** — minimum viable **manual** + **one end-to-end guide** + **API index** before calling the platform “1.0”; then iterative expansion until the scope above is covered.
- **`pyproject.toml` / PyPI URLs** — **Documentation** link pointing at RTD **stable** once the first public release of the site ships.

---

# Phase 5 — Ecosystem Expansion

## Goals
- Expand beyond Streamlit-only rendering

## Features
- FastAPI renderer
- Static HTML renderer
- Alternate runtime support
- Plugin architecture (optional backends and extras register through StreamTree, not ad-hoc direct imports)
- **Cross-runtime patterns** — where feasible, carry forward error boundaries, context, and memo semantics behind the multi-renderer abstraction so plugins do not bypass safety rails
- **Async-native renderer hooks** — backends (e.g. FastAPI) may supply **async** data providers; contract for how they feed the virtual tree or session state without assuming a Streamlit-only thread model
- **FastAPI + asyncio** — document recommended patterns for sharing async clients and task lifetimes with Streamlit sessions when both appear in one product

## Deliverables
- Multi-renderer abstraction
- Plugin SDK
- Extension registry
- **Async-capable plugin contract** — typed hooks for async setup/teardown where the host runtime supports it

---

# Long-Term Vision

StreamTree becomes:
- the architecture layer for Streamlit
- a Python-native UI framework ecosystem
- a production-grade application platform where **full apps can be authored and run through StreamTree’s own workflow** (CLI + templates + runner helpers), with **Streamlit as the default execution engine** and **direct `streamlit run` always available** for those who want it
- a project whose **user manual, guides, and API reference** live on **Read the Docs** as the canonical, versioned learning surface (see [Documentation platform](#documentation-platform-read-the-docs))

Potential ecosystem packages:
- streamtree-auth
- streamtree-testing
- streamtree-fastapi
- streamtree-admin
- streamtree-charts
- streamtree-enterprise
- streamtree-async (optional split if `streamtree.asyncio` grows large enough to warrant its own installable package)

These packages should reuse the **Patterns from React ergonomics** section above where applicable (e.g. testing and admin UIs benefit most from tree introspection, error boundaries, memoized data surfaces, and **async task orchestration**).
