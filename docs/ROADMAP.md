
# StreamTree Roadmap

This document tracks **product direction and phased delivery**. It aligns with [DEPENDENCY_STRATEGY.md](./DEPENDENCY_STRATEGY.md) (optional extras, wrapper-first APIs) and [PLAN.md](./PLAN.md#async-model-first-class-data-plane) (async + rerun model). **CHANGELOG** records what actually shipped per version.

## How to use this roadmap

1. **Release index** (table below) — snapshot of phases and what has **shipped in tagged releases** (PyPI publishes when the [release workflow](https://github.com/streamtree-dev/streamtree/blob/main/.github/workflows/release.yml) succeeds on **`v*.*.*`** tags).
2. **Near-term themes** — backlog and cross-cutting work (docs, CLI, helpers) that span releases.
3. **Pattern catalog** — design vocabulary mapped to phases (not a separate product spec).
4. **Phase 0–5** — historical goals and long-range bets; detailed **shipped vs open** for Phase 2 lives in the table + backlog, not duplicated in the Phase 2 feature list.

**Contents:** [Release index](#release-index) · [Phase 2 backlog & themes](#phase-2-backlog--near-term-themes) · [Patterns](#patterns-from-react-ergonomics-non-vdom-rerun-native) · [Phase 0](#phase-0--foundation) · [Phase 1](#phase-1--mvp) · [Phase 2](#phase-2--application-features) · [Phase 3](#phase-3--data-application-toolkit) · [Phase 4](#phase-4--testing-and-tooling) · [Documentation (RTD)](#documentation-platform-read-the-docs) · [Phase 5](#phase-5--ecosystem-expansion) · [Vision](#long-term-vision)

---

## Release index

_Last updated: 2026-05-12._

| Track | Status | Notes |
|-------|--------|--------|
| Phase 0 — Foundation | **Complete** | Package layout, Streamlit renderer, design docs in `docs/`. |
| Phase 1 — MVP | In progress | **0.1.0** core tree + state; **0.2.0** Pydantic + stub extras; deeper memoization / `streamlit-extras` curation still open. |
| Phase 2 — Application | In progress | **Shipped through 0.7.0:** same as **0.6.0** plus **`streamtree.asyncio`** **`submit_many`**, cooperative cancel helpers, and stale-key docs (**0.7.0**). **Next:** navigation polish, portals, more **`streamlit-extras`** names, further async orchestration, **`streamtree init`** templates — see [PHASE2_TAIL.md](./PHASE2_TAIL.md). |
| Phase 3 — Data toolkit | Planned | Tables, charts, performance playbooks; follows Phase 2. |
| Phase 4 — Tooling | Planned | Testing, dev introspection; **`streamtree` CLI** MVP shipped in **0.4.0**; overlaps RTD handoff. |
| Docs — Read the Docs | Planned | [Manual, guides, API](#documentation-platform-read-the-docs); **stable** / **latest**; CI doc builds. |

### 0.7.0 (shipped)

- **`streamtree.asyncio`:** **`submit_many`** for parallel independent tasks; cooperative cancellation (**`TaskHandle.cancel()`** on running work sets **`cancel_requested`**; **`is_task_cancel_requested`** / **`complete_cancelled`** for workers); **`mark_done`** respects worker-initiated **cancelled**; module docstring covers **stale keys** (same `key` = same logical task across reruns).

### 0.6.0 (shipped)

- **`streamtree init`:** scaffold **`app.py`** (+ optional **`pages/`**) via **`[cli]`**; **`streamtree.helpers.scaffold`**.
- **`AuthGate`** + **`streamtree.auth.build_authenticator`** behind **`[auth]`** (`streamlit-authenticator`).
- **`Dialog`** / **`Popover`** overlay elements; Streamlit **≥ 1.33** dependency floor.
- **`[ui]`:** **`ColoredHeader`**, **`VerticalSpaceLines`** (`streamlit-extras` wrappers).
- **Docs / tests:** [`PHASE2_TAIL.md`](./PHASE2_TAIL.md); expanded renderer and CLI coverage.

### 0.5.0 (shipped)

- **`streamtree.helpers.pages`:** `PageEntry`, `pages_dir_next_to`, `list_page_entries`, `discover_pages` for Streamlit `pages/` scripts (labels + sort keys + `PageLink` paths); exported from **`streamtree.helpers`**.
- **`streamtree.asyncio`:** `set_task_progress` and **`TaskHandle.progress()`**; task session dict stores **`progress`** (lock-serialized with status/result/error).
- **Examples:** **`examples/pages_helpers_demo.py`**, stub **`examples/pages/1_About_demo.py`**.
- **Docs:** README install pin + capabilities, [PLAN.md](./PLAN.md) packaging line, [DEPENDENCY_STRATEGY.md](./DEPENDENCY_STRATEGY.md) (`helpers.pages` + progress), this roadmap’s release index / Phase 2 “Next”.
- **Tests:** expanded coverage for **`helpers.pages`** (paths, unicode, ordering, in-directory symlinks) and **`asyncio`** progress (poll while running, error path, main-thread updates).

### 0.4.1 (shipped)

- **Patch:** version **0.4.1**; README / changelog release metadata; CI badge target alignment (fork).

### 0.4.0 (shipped)

- **CLI:** optional **`[cli]`** (Typer) + **`streamtree run`** / **`streamtree doctor`**; delegates to **`streamlit run`**.
- **`streamtree.helpers.runner`:** argv builder + **`run_streamlit_sync`** (stdlib). **`[runner]`** extra remains a metadata stub; **`[pages]`** reserved for multipage helpers.
- **`PageLink`** + **`st.page_link`** renderer path; **Streamlit ≥ 1.30** required.
- **`App`:** **`initial_sidebar_state`**, **`menu_items`** for **`st.set_page_config`**.
- **Forms:** **`bind_numeric_fields`**, **`number_inputs`**, **`numeric_field_names`**.
- **Examples:** **`examples/numeric_nav_demo.py`**, **`examples/streamtree_run_demo.md`**.

### 0.3.0 (shipped)

- **`streamtree.app`:** `App`, `apply_page_config`, `app_root_element`, `render_app()` (guarded `st.set_page_config`).
- **`streamtree.theme`:** `Theme`, `theme()` / `theme_css()`, `ThemeRoot` + `provider(theme=...)`.
- **`streamtree.asyncio`:** `submit` / `TaskHandle` (stdlib threads; `[asyncio]` slot for future backends).
- **`streamtree.forms`:** `bind_str_fields`, `str_text_inputs`.
- **Examples:** `examples/app_shell.py`, `examples/async_bg.py`, `examples/model_form.py`.

### 0.2.0 (shipped)

- **Deps:** Pydantic v2, typing-extensions; stub extras (`tables`, `charts`, `ui`, `auth`, `asyncio`, `async`, `cli`, `all`); `[async]` aliases `[asyncio]` in `pyproject.toml`.
- **Routing:** `sync_route`, `set_route`, `Routes` (`examples/routed_app.py`).
- **`ErrorBoundary`**, **`app_context`**, forms slice (`str_field_names`, `model_validate_json`, `format_validation_errors`).

---

## Phase 2 backlog & near-term themes

### Backlog (post-0.6.0)

- Richer **App** / **navigation** (beyond shell + `Routes` + `PageLink` + `init` template).
- **Auth** hardening and alternative providers (beyond **`streamlit-authenticator`**).
- **Portals**, **imperative handles**, **route prefetch**, richer **async orchestration** beyond progress (e.g. composition, cancellation UX) on `streamtree.asyncio`.
- **More** **`streamlit-extras`** curation behind stable StreamTree names (see [`PHASE2_TAIL.md`](./PHASE2_TAIL.md)).
- **Form builder** beyond string + scalar numeric fields (layout, batch submit).

### Optional dedicated helpers

Reserved **empty extras** (same pattern as **`[pages]`**) until deps/APIs are pinned:

- **`[pages]`** — optional extra stays **empty** until pinned third-party deps land; **`streamtree.helpers.pages`** (stdlib discovery) ships in the default install as of **0.5.0** — multipage / `pages/` + navigation APIs ↔ **`Routes`**, **`App`**; Streamlit version matrix; **no second web server**.
- **`[runner]`** — metadata-only companion to **`streamtree.helpers.runner`** (stdlib **`streamlit run`** helpers ship in the default install; **`[cli]`** adds Typer for the **`streamtree`** console script).

### End-to-end app experience (optional Streamlit CLI)

**Goal** — One StreamTree-shaped workflow (scaffold → configure → run) **without** requiring the Streamlit CLI for teams that opt in.

- **Always supported:** `streamlit run app.py` (CI, debugging, power users).
- **Shipped (0.4.0):** **`streamtree run`** / **`streamtree doctor`** behind **`pip install "streamtree[cli]"`**, delegating to **`python -m streamlit run`** (see **`streamtree.helpers.runner`**).
- **Shipped (0.6.0):** **`streamtree init`** for **`app.py`** (+ optional **`pages/`**).
- **Boundary:** DX/packaging layer in Phases 2–4, not a new server. “No Streamlit CLI” = **no obligation to use Streamlit’s CLI**, not removing Streamlit from the stack.
- **Docs:** Full manual/guides on **RTD** ([Documentation platform](#documentation-platform-read-the-docs)); README stays short.

---

## Patterns from React ergonomics (non-VDOM, rerun-native)

StreamTree is **not** React and will **not** ship a browser VDOM. The list below maps **product patterns** to **Streamlit’s rerun model** (see phase column).

1. **Error boundaries** — subtree failures → fallback UI + logging.
2. **Context / DI** — theme, tenant, flags, route data without prop drilling.
3. **Stable list identity / keys** — dynamic children stay aligned across reruns.
4. **Subtree memoization** — skip rebuilding when inputs unchanged.
5. **Transitions / deferred regions** — lower-priority or chunked regions under load.
6. **Suspense-shaped async** — loading / ready / error UI for async-shaped work (rerun-native).
7. **Imperative handles** — focus, scroll, etc., where Streamlit allows; document limits.
8. **Portals / layout targets** — attach subtrees to sidebar, dialog, etc.
9. **Dev introspection** — tree, props, bound `session_state` keys.
10. **Async task orchestration** — submit off-thread, **poll** on rerun; optional progress ([asynclit](https://github.com/eddiethedean/asynclit)-class integrations behind `streamtree.*` when applicable).

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

## Phase 0 — Foundation

### Goals

- Package architecture, core rendering, developer ergonomics.
- **Dependency philosophy:** small hard set; heavy stacks **opt-in** via extras.

### Deliverables

- Element model, `@component`, tree + Streamlit renderer.
- Minimal docs; pattern philosophy tied to [Patterns](#patterns-from-react-ergonomics-non-vdom-rerun-native).
- Async + rerun narrative + pointers to [PLAN.md](./PLAN.md#async-model-first-class-data-plane).
- **`pyproject.toml`** install tiers documented (`streamtree`, `[tables]`, …, `[pages]`, `[runner]` when added, `[dev]`, `[all]`).

---

## Phase 1 — MVP

### Goals

- Usable framework on Streamlit; core layouts and state.

### Features (checklist)

**Elements:** Text, Markdown, Button, TextInput, NumberInput, SelectBox, Checkbox, DataFrame, Image.

**Layouts:** VStack, HStack, Grid, Columns, Tabs, Sidebar, Form, Card.

**State:** `state`, `toggle_state`, `form_state`, `session_state`.

**Rendering:** `render`, component identity, key discipline.

**Rerun-native:** keyed dynamic lists; subtree memo hooks where MVP allows; documented loading branches (`loading` / `ready` / `error`) without blocking `render`.

**Async (guidance):** when to use `st.cache_data` / fragments vs future **`streamtree.asyncio`**.

### Dependency alignment (MVP)

- Hard deps per strategy; Pydantic for props/forms where scope allows.
- Curated `streamlit-extras` only behind stable `streamtree.*` names.

### Deliverables

- pip-installable package, examples, demos.
- Stub extras in `pyproject.toml` (`tables`, `charts`, `ui`, `auth`, `async`, `cli`, `pages`, `runner`, `all`) as names are reserved.
- Optional `[async]` integration path documented even if not default-installed yet.

---

## Phase 2 — Application features

### Goals

- Production-grade apps on Streamlit: routing, resilience, theming, async slice, forms.

### Completed (through 0.6.0)

The following Phase 2 themes are **done** for the current minor line; details and version pins live in the [Release index](#release-index).

- **Routing & resilience:** `sync_route` / `set_route`, `Routes`, `ErrorBoundary`, `app_context`.
- **Forms:** Pydantic-first string + scalar numeric bindings and inputs.
- **App shell:** `App`, `apply_page_config`, `render_app`, sidebar composition, `PageLink` + `st.page_link`, `initial_sidebar_state` / `menu_items` passthrough.
- **Theming:** `Theme` / `theme()` / `ThemeRoot`.
- **Async worker slice:** `streamtree.asyncio` `submit` / `TaskHandle`, session task dict, **progress** field + **`set_task_progress`** / **`TaskHandle.progress()`**.
- **Run / multipage DX (stdlib):** `streamtree.helpers.runner`, optional **`[cli]`** `streamtree run` / `doctor` / **`init`**, **`streamtree.helpers.pages`** for `pages/` discovery.
- **Optional auth:** **`AuthGate`** + **`[auth]`** (`streamlit-authenticator`).
- **Overlays:** **`Dialog`**, **`Popover`** (Streamlit-native; version floor **1.33**).
- **Optional UI extras:** **`[ui]`** first wrappers (`ColoredHeader`, `VerticalSpaceLines`).

### Release notes

Shipped scope for **0.2.0** through **0.6.0** is in the [Release index](#release-index) and subsections above. **Open** work is in the [backlog](#phase-2-backlog--near-term-themes) and [PHASE2_TAIL.md](./PHASE2_TAIL.md).

### Optional dependency alignment

- **`[auth]`:** e.g. `streamlit-authenticator` behind `AuthProvider` / protected routes; document limits.
- **`[ui]`:** shadcn-style / `extra-streamlit-components` only behind StreamTree components.
- **`[async]` (when shipped):** optional backend (e.g. asynclit) **only** via **`streamtree.asyncio`** public API.

### Deliverables (remaining / stretch)

Everything listed under **Completed (through 0.6.0)** above is **closed** for the current release line; items below are still **open**.

- Deeper navigation framework, auth, portals, richer theme/forms/async as backlog clears.
- Example apps for error boundaries + context + parallel loads + async UI branches.

---

## Phase 3 — Data application toolkit

### Goals

- Best architecture layer for **data-heavy** Streamlit apps.

### Features

- Tables, CRUD patterns, filters, query-state, dashboards, chart wrappers.
- Memo for expensive branches; deferred regions; async loaders + **`streamtree.asyncio`** `gather`-style composition; declarative loader + ready/loading/error subtrees.

### Optional dependency alignment

- **`[tables]`:** e.g. `streamlit-aggrid` → `DataGrid`.
- **`[charts]`:** plotly / echarts / altair → declarative chart elements.
- **`[async]`:** worker-loop integration; docs stay on **`streamtree.asyncio`**.

### Deliverables

- Templates, exploration toolkit, enterprise-oriented components.
- Performance playbook; **`streamtree.asyncio`** reference (cancellation, stale-run rules).

---

## Phase 4 — Testing and tooling

### Goals

- Enterprise workflows: testing, CLI, introspection, **StreamTree-first run** (optional), **RTD** as canonical learning surface.

### Features

- Snapshot / `render_to_tree` JSON workflows; component tree visualization; dev introspection; in-flight async inspection in dev.
- **Typer `streamtree` CLI** (`[cli]`): **`run` / `serve`**, `preview`, `doctor`, `tree`, optional **`init`**.
- Storybook-style previews, visual regression, state inspection helpers.

### Optional dependency alignment

- **`[dev]`:** pytest, ruff, **ty** (CI typecheck), **mypy** (optional local contributor toolchain).
- **`[cli]`:** typer + minimal deps; **`streamlit run`** remains documented fallback.

### Deliverables

- pytest + preview server + introspection surfaces; async testing kit (e.g. AppTest patterns).
- **`streamtree` entry point** + non-interactive flags; **RTD ↔ CLI** copy alignment ([Documentation platform](#documentation-platform-read-the-docs)).

---

## Documentation platform (Read the Docs)

### Goals

- **Versioned, searchable** docs on [**Read the Docs**](https://readthedocs.org/) as the **primary** learning path (README + `docs/*.md` stay summaries / design depth).

### Scope (rolled out over several releases)

**User manual:** concepts (rerun model, trees vs `st.*`, `@component`, keys, `render` / `render_app`, `App`); core libs; optional extras matrix + Streamlit version notes; interop + deployment.

**How-to guides:** first full app; routing; forms; async; **lifecycle** tutorials once `streamtree run` / `init` exist ([End-to-end](#end-to-end-app-experience-optional-streamlit-cli)).

**API reference:** autodoc (Sphinx or MkDocs/mkdocstrings—decision in-repo); intersphinx to Streamlit / Pydantic / stdlib; stable per-symbol URLs.

**Operations:** stable vs **latest** policy tied to tags/PyPI; **PR doc builds** with fail-on-broken-links where feasible; contributor preview + prose styleguide.

### Deliverables

- RTD project + webhooks; site skeleton (Manual · Guides · API · release notes link).
- **MVP:** minimal manual + one end-to-end guide + API index before “1.0”; then flesh out scope above.
- PyPI **Documentation** URL → RTD **stable** when the site goes public.

---

## Phase 5 — Ecosystem expansion

### Goals

- Optional **non-Streamlit** renderers and plugin ecosystem.

### Features

- FastAPI / static HTML renderers; plugin registry; cross-runtime error/context/memo semantics where feasible; async-native data hooks for alternate hosts; FastAPI + Streamlit coexistence patterns.

### Deliverables

- Multi-renderer abstraction, plugin SDK, extension registry, async-capable plugin contract.

---

## Long-term vision

StreamTree becomes:

- The **architecture layer** for Streamlit-first apps.
- A **Python-native** UI ecosystem with optional heavier runtimes.
- A **production application platform**: optional **StreamTree CLI + templates + runner** for create/run, **Streamlit as default engine**, **`streamlit run` always available**.
- A project whose **manual, guides, and API reference** live on **Read the Docs** ([above](#documentation-platform-read-the-docs)).

**Potential spin-out packages:** `streamtree-auth`, `streamtree-testing`, `streamtree-fastapi`, `streamtree-admin`, `streamtree-charts`, `streamtree-enterprise`, optional `streamtree-async` if `streamtree.asyncio` grows large enough.

Reuse [Patterns](#patterns-from-react-ergonomics-non-vdom-rerun-native) for testing, admin, and async-heavy surfaces.
