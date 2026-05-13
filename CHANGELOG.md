# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.11.0] — 2026-05-13

### Added

- **CLI (`[cli]`):** **`streamtree tree`** (`module:attr`, **`--format`**, **`--summarize`**, **`--expand-components`**); **`streamtree preview`** and **`streamtree serve`** as aliases of **`run`**; **`streamtree doctor --verbose`**.
- **`streamtree.helpers.tree_target.load_element_from_target`** for resolving **`module:attr`** trees.
- **`streamtree.testing.viz`:** **`format_tree_text`**, **`tree_dict_to_mermaid`** for human-readable tree views.
- **`streamtree.testing.introspection`:** **`iter_streamtree_session_keys`**, **`summarize_streamtree_session_state`**.
- **`streamtree.testing.apptest.run_app_function`** wrapper around **`AppTest.from_function(...).run`**.
- **`streamtree.asyncio.summarize_async_tasks`** for read-only summaries of managed task slots.
- **`streamtree.debug_render_path`** (re-exported from **`streamtree.core.context`**).
- **Docs:** **`docs/TESTING_AND_DEBUG.md`**; MkDocs **API reference** pages (**mkdocstrings**); **`.readthedocs.yml`** for Read the Docs builds.
- **`examples`:** package **`__init__.py`** and **`examples.counter.streamtree_tree_root`** for **`streamtree tree`** demos.
- **`tests/test_examples_run.py`:** **`AppTest.from_file`** smoke test for every **`examples/*.py`** and **`examples/pages/*.py`** script (asserts no **`at.exception`** entries); **`echarts_demo.py`** is skipped because **`streamlit-echarts`** custom-component registration fails in the AppTest harness.

### Fixed

- **CI:** **`ruff format --check`** — apply Ruff formatting to **`tests/test_tree_viz.py`** (was failing **`lint-test`** matrix on push).
- **`examples/crud_pattern_demo.py`:** form actions use **`Button(..., submit=True)`** so Streamlit receives **`st.form_submit_button`** instead of **`st.button`** inside **`st.form`**.
- **`examples/numeric_nav_demo.py`:** **`PageLink`** targets **`pages/1_About_demo.py`** (a valid multipage path relative to the entrypoint; sibling **`counter.py`** is not a discoverable page for **`st.page_link`**).

### Documentation

- **`docs/EXAMPLES.md`:** MkDocs / Read the Docs page with **embedded full source** for every **`examples/*.py`** and **`examples/streamtree_run_demo.md`** (via **`pymdownx.snippets`**).
- **`docs/recipes/`:** Cookbook pages (first app, state, forms, routing, async, multipage, shell/theme, layouts, data extras, CRUD, auth, CLI, portals, organization, observability, Streamlit interop).
- **MkDocs Material:** **`mkdocs-material`** theme, tabbed nav (**Home**, **Examples**, **Recipes**, **Guides**, **API reference**), extended Markdown (**admonitions**, **details**, **tabbed**, **highlight**, **emoji**, **tables**), **`docs/getting-started.md`**, redesigned **`docs/index.md`**, **`docs/stylesheets/extra.css`**, **`site_url`** / **`edit_uri`**; **Guides** split into **Design & roadmap** vs **Operations**; nested **API reference**; **ROADMAP** internal anchors updated for Material heading slugs.
- **README:** shortened for PyPI / GitHub; **Read the Docs** as the primary learning surface with a compact doc map and RTD links.
- **Docs URLs:** **PyPI** **Documentation**, **MkDocs** **`site_url`**, and **README** RTD links use **`/en/latest/`** (shields **docs** badge uses **`readthedocs/streamtree/latest`**) because **`stable`** is not yet serving; roadmap notes **`stable`** when versioned RTD builds are active.

## [0.10.0] — 2026-05-13

### Added

- **`AltairChart`** (`[charts]` extra): Altair specs via **`st.altair_chart`**; **`altair`** pinned alongside **`plotly`** in **`[charts]`** / **`[all]`** / **`[dev]`**.
- **`EChartsChart`** (`[charts]` extra): ECharts option dicts via **`streamlit_echarts.st_echarts`**; **`streamlit-echarts`** pinned with **`plotly`** and **`altair`** in **`[charts]`** / **`[all]`** / **`[dev]`**.
- **`DataGrid.on_result`**: optional callback invoked once after a successful **`AgGrid`** call with the grid return value (selection / updates); not called if **`AgGrid`** raises.
- **`streamtree.loading.match_task_many`**: declarative subtree when **all** pollable handles are **`done`**, with **any-error** and **any-cancelled** semantics (see docstring and **`docs/PERFORMANCE.md`**).
- **`streamtree.loading.submit_many_ordered`**: start **`submit_many`** jobs in **sorted key order** so **`match_task_many`** result tuples are stable.
- **`streamtree.state.memo_subtree`**: memoize values keyed by render path + logical key + **`deps`** fingerprint (see **`docs/PERFORMANCE.md`**).
- **`streamtree.elements.DeferredFragment`**: defer child rendering with **`st.fragment`** when the Streamlit version exposes it.
- **`streamtree.crud`**: **`selected_id_from_query`**, **`save_intent_counter`** for list/detail/save flows (not a full admin framework).
- **`streamtree.enterprise`**: optional **`EventSink`** via **`app_context`**, **`emit_event`**, **`tenant_id`**, **`redact_secrets`** (no extra pinned vendors).
- **`streamtree.perf`**: **`perf_bump`** / **`perf_snapshot`** with **`PERF_COUNTERS_KEY`** in **`app_context`** for lightweight counters.
- **`streamtree.helpers.explore`**: **`column_summary`** (stdlib); **`dataframe_profile`** when pandas is present (**`[tables]`**).
- **`streamtree.testing.summarize_tree_kinds`**: count element **`kind`** values in **`render_to_tree`** output.
- **CLI:** **`streamtree init --template`** / **`-t`** for **`default`**, **`crud`**, **`explore`**, **`enterprise`** scaffolds.
- **Docs:** **`docs/PHASE3_CRUD.md`** — Phase 3 list/detail/save patterns with **`DataGrid`**, routing, async, **`match_task`** / **`match_task_many`**; **`docs/PERFORMANCE.md`** updates for large trees and hooks.
- **Example:** **`examples/altair_chart_demo.py`**, **`examples/crud_pattern_demo.py`**, **`examples/crud_automation_demo.py`**, **`examples/echarts_demo.py`**, **`examples/datagrid_selection_demo.py`**, **`examples/deferred_region_demo.py`**, **`examples/async_ordered_loader_demo.py`**.

### Changed

- **`streamtree.__version__`** reads **`importlib.metadata.version("streamtree")`** so it tracks **`pyproject.toml`** for editable installs, wheels, and PyPI (cross-checked in **`tests/test_package_meta.py`**).
- **CI:** Windows matrix pins **`windows-2025-vs2026`** instead of **`windows-latest`** to avoid image redirect notices.
- **Release workflow:** tag builds publish to **PyPI** and **GitHub Packages** (see **`.github/workflows/release.yml`**).

## [0.9.0] — 2026-05-13

### Added

- **`streamtree.portals`:** **`gather_portals`**, **`portal_render_context`**, **`take_portal_children`**; layout elements **`Portal`**, **`PortalMount`** (named-slot deferred rendering; see **`docs/PHASE2_PORTALS_AND_PREFETCH.md`**).
- **`SplitView`** layout (narrow + main column strip, pseudo-sidebar without a second **`st.sidebar`**).
- **`streamtree.helpers.pages`:** **`iter_page_entries`**, **`prefetch_page_sources`** (optional **`compile()`** syntax warm-up for page scripts without importing modules); **`group_page_entries_by_order_prefix`**, **`page_links_sidebar_sections`**, **`multipage_sidebar_nav`** (sectioned sidebar nav).
- **`streamtree.forms_layout`:** **`model_field_grid`**, **`build_model_from_bindings`** for row/column Pydantic forms (including **bool** fields); **`bool_field_names`**, **`bind_bool_fields`** in **`streamtree.forms`**; doc **`docs/PHASE2_FORMS.md`**.
- **`[ui]`** elements **`BottomDock`** (bottom container), **`FloatingActionButton`**, **`Stoggle`**, **`TaggerRow`**, **`MentionChip`** (streamlit-extras).
- **Routing:** **`clear_query_param`**, **`clear_route`**, **`update_query_params`** for URL/session cleanup and multi-key updates.
- **Async:** **`dismiss_tasks`** batch terminal cleanup.
- **Docs:** **`docs/PHASE2_PORTALS_AND_PREFETCH.md`** (Phase 2 portals / prefetch / form-layout contract); **`docs/PHASE2_TAIL.md`** reconciliation; roadmap Phase 2 closure.
- **Example:** **`examples/phase2_composite_demo.py`** (ErrorBoundary, `app_context`, `Routes`, `submit_many`).

### Changed

- **`streamtree.core.component.render` / `render_app`** now run the Streamlit backend’s **`render()`** wrapper so portal gather runs once per tree.

## [0.8.0] — 2026-05-13

### Added

- **`streamtree.helpers.pages.page_links`:** build **`PageLink`** tuples from **`discover_pages`** / **`list_page_entries`** output (navigation coupling with multipage apps).
- **`streamtree.asyncio.dismiss_task`:** remove a **terminal** task session entry so **`submit`** can reuse the same ``key``.
- **`[ui]`** elements **`SocialBadge`** (streamlit-extras badges) and **`StyleMetricCards`** (metric card CSS helper).
- **`streamtree init --with-pages`:** generated **`app.py`** now wires **`discover_pages`** + **`page_links`** into a **`SidebarNav`** shell.
- **`[tables]`** optional extra: **`streamlit-aggrid`** + **`DataGrid`** element and **`streamtree.tables.render_datagrid`** (lazy import with install hint).
- **`[charts]`** optional extra: **`plotly`** + **`Chart`** element and **`streamtree.charts.render_chart`** (Plotly via **`st.plotly_chart`**).
- **`streamtree.routing.sync_query_value`** / **`set_query_value`**: URL ↔ session helpers for arbitrary string query params (including empty defaults), complementing **`sync_route`** / **`set_route`**.
- **`streamtree.loading.match_task`**: map **`TaskHandle.status`** to **`loading` / `ready` / `error` (and optional `cancelled`)** element subtrees.
- **Examples:** **`examples/datagrid_demo.py`**, **`examples/chart_demo.py`**, **`examples/async_loader_demo.py`**.
- **Docs:** [`docs/PERFORMANCE.md`](https://github.com/streamtree-dev/streamtree/blob/main/docs/PERFORMANCE.md) playbook for memoization, async work, URL filters, and optional data extras.

### Changed

- **`[all]`** meta-extra now lists **`streamlit-aggrid`**, **`plotly`**, and the existing optional CLI/auth/UI pins for convenience.
- **`[dev]`** includes **`streamlit-aggrid`** and **`plotly`** so contributor / CI installs exercise optional render paths.

## [0.7.1] — 2026-05-13

### Changed

- **Packaging:** version **0.7.1** (patch).

### Documentation

- **README:** CI badge and Actions link use **`eddiethedean/streamtree`** so Shields.io reflects this fork’s workflow status.

## [0.7.0] — 2026-05-12

### Added

- **`streamtree.asyncio.submit_many`:** start several independent tasks with unique keys (gather-style composition).
- **Cooperative cancel:** **`TaskHandle.cancel()`** on a **running** task sets **`cancel_requested`**; workers poll **`is_task_cancel_requested`** and call **`complete_cancelled`** to finish as **cancelled**; normal **done** still wins if the worker completes without acknowledging cancel.

### Documentation

- **`streamtree.asyncio`:** module docstring sections **Stale runs and keys** and **Cooperative cancellation**; [README.md](https://github.com/streamtree-dev/streamtree/blob/main/README.md) background-work bullet; [PHASE2_TAIL.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/PHASE2_TAIL.md) / [ROADMAP.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md) release notes.
- **`examples/async_bg.py`:** demonstrates **`submit_many`**.

## [0.6.0] — 2026-05-12

### Added

- **CLI (`[cli]`):** **`streamtree init`** scaffolds **`app.py`** and optional **`pages/`** (see **`streamtree.helpers.scaffold`**).
- **Auth (`[auth]`):** **`streamtree.auth.build_authenticator`**, **`AuthGate`** element (in **`streamtree.elements.auth_gate`**), and Streamlit renderer integration for **`streamlit-authenticator`**.
- **Overlays:** **`Dialog`** and **`Popover`** layout elements (``st.dialog`` / ``st.popover`` with fallbacks); **`streamlit>=1.33.0`** core floor.
- **UI extras (`[ui]`):** **`ColoredHeader`** and **`VerticalSpaceLines`** wrapping **`streamlit-extras`** (lazy import + install hint).
- **Examples:** **`examples/overlay_demo.py`**, **`examples/auth_demo.py`**.
- **Docs:** [`docs/PHASE2_TAIL.md`](https://github.com/streamtree-dev/streamtree/blob/main/docs/PHASE2_TAIL.md) for post-0.6.0 Phase 2 grooming.

### Changed

- **Dependencies:** **`streamlit>=1.33.0`**; **`[auth]`** pins **`streamlit-authenticator`**, **`[ui]`** pins **`streamlit-extras`**; **`[dev]`** includes both for contributor / CI installs.
- **`session_state(..., default=None)`:** first read on a missing key raises **`ValueError`** with a hint instead of a bare **`KeyError`**.
- **`streamtree.helpers.scaffold.app_py_source`:** embeds **`page_title`** via **`repr()`** so generated **`app.py`** stays valid for arbitrary titles.
- **`streamtree.asyncio`:** **`TaskHandle`** and **`set_task_progress`** only touch task dicts that include a real **`threading.Lock`** (same shape as **`submit`**); fake **`_submitted`** entries without a lock are replaced on **`submit`**.
- **`ErrorBoundary`:** if **`on_error`** raises, the error is logged and **`fallback`** is still rendered.

### Documentation

- README: **0.6.0** pin, Streamlit **1.33+**, **`streamtree init`**, auth / overlay / **`[ui]`** capabilities; releases tag **`v0.6.0`**; overlay bullet clarifies **`Dialog`** legacy (inline) vs **`Popover`** (expander) fallbacks.
- [ROADMAP.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md), [PLAN.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/PLAN.md), [DEPENDENCY_STRATEGY.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md): **0.6.0** shipped scope and optional-extra notes ( **`[all]`** was documented as an empty stub until **0.8.0** populated the meta-extra).
- **`Dialog`**, **`App` / `apply_page_config`:** docstrings for legacy dialog behavior and one-shot **`st.set_page_config`** per session.

## [0.5.0] — 2026-05-12

### Added

- **`streamtree.helpers.pages`:** `PageEntry`, `pages_dir_next_to`, `list_page_entries`, and `discover_pages` for Streamlit `pages/` discovery (stdlib + pathlib); re-exported from **`streamtree.helpers`**.
- **`streamtree.asyncio`:** `set_task_progress` and **`TaskHandle.progress()`** for lock-safe, rerun-polled worker progress (task dict includes `progress`).
- **Example:** `examples/pages_helpers_demo.py` with `examples/pages/1_About_demo.py` stub page.
- **Tests:** expanded coverage for **`streamtree.helpers.pages`** (paths, unicode, ordering, symlinks) and **`streamtree.asyncio`** progress (poll while running, error path, main-thread updates).

### Documentation

- README: **0.5.0** install pin, capabilities for multipage helpers + async progress, example command; releases tag example **`v0.5.0`**.
- [ROADMAP.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md): release index **0.5.0**; Phase 2 “Next” backlog adjusted.
- [PLAN.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/PLAN.md): packaging timeline **0.5.0** bullet.
- [DEPENDENCY_STRATEGY.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md): asyncio progress note; **`helpers.pages`** + **`[pages]`** stub subsection.

## [0.4.1] — 2026-05-12

### Changed

- **Packaging:** version **0.4.1** (patch); README install pin and release tag example updated to **`v0.4.1`**.

## [0.4.0] — 2026-05-12

### Added

- **CLI (optional `[cli]`):** **`streamtree run`** delegates to **`python -m streamlit run`** with forwarded argv; **`streamtree doctor`** prints versions and Typer availability. **`[project.scripts]`** entry **`streamtree`**.
- **`streamtree.helpers.runner`:** **`build_streamlit_run_argv`**, **`run_streamlit_sync`** (stdlib subprocess; **`FileNotFoundError`** → exit code **127**; empty args → **2**).
- **`PageLink`** element mapping to **`st.page_link`** (Streamlit **≥ 1.30** in core dependencies).
- **`App`:** **`initial_sidebar_state`** and **`menu_items`** passed through to **`st.set_page_config`** when set.
- **`streamtree.forms`:** **`numeric_field_names`**, **`bind_numeric_fields`**, **`number_inputs`** for **`int`** / **`float`** and optional numeric fields.
- Example **`examples/numeric_nav_demo.py`** and **`examples/streamtree_run_demo.md`** (CLI usage).

### Changed

- **Minimum Streamlit** raised to **`>=1.30.0`** (for **`st.page_link`**).
- **`[cli]`** extra now lists **Typer**; stub extras **`[pages]`** and **`[runner]`** documented (runner helper ships in the default install; **`[runner]`** remains metadata-only).

### Documentation

- README: **`streamtree[cli]`**, **`streamtree run`**, Streamlit **1.30+** requirement, **`v0.4.0`** release tag example.
- [DEPENDENCY_STRATEGY.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/DEPENDENCY_STRATEGY.md): CLI / **`[pages]`** / **`[runner]`** notes.
- [ROADMAP.md](https://github.com/streamtree-dev/streamtree/blob/main/docs/ROADMAP.md): **0.4.0** release index; Phase 2 “Next” adjusted.

### Fixed

- **CI:** **`cli-smoke`** sets job-level **`UV_PYTHON`** so **`uv run streamtree doctor`** reuses the **`[cli]`** sync environment (otherwise **`uv run`** could follow **`.python-version`** and miss Typer).

## [0.3.0] — 2026-05-12

### Added

- **Packaging:** optional extra **`[async]`** as a TOML-quoted alias of the empty **`[asyncio]`** stub extra (matches install examples in the plan and dependency strategy).
- **`streamtree.app.App`** shell with optional sidebar composition, **`apply_page_config`**, **`app_root_element`**, and **`render_app()`** (one-time `st.set_page_config` guard).
- **`streamtree.theme`**: **`Theme`** (Pydantic), **`theme()`** / **`theme_css()`**, and **`ThemeRoot`** element for CSS injection via `app_context.provider(theme=...)`.
- **`streamtree.asyncio`**: **`submit()`** / **`TaskHandle`** for daemon-thread background work with session-scoped poll keys (stdlib-only; optional `[asyncio]` / `[async]` stub extras unchanged as meta).
- **`streamtree.forms`**: **`bind_str_fields`** and **`str_text_inputs`** for declarative `TextInput` grids from Pydantic string fields.
- Examples **`examples/app_shell.py`**, **`examples/async_bg.py`**, **`examples/model_form.py`**.

### Changed

- **Routing:** `sync_route` / `set_route` now store the active route in `st.session_state` under `streamtree.routing.active.<param>` (one slot per query-param name) instead of a single global `streamtree.routing.active` key. Apps that read that private key must migrate.
- **`ErrorBoundary.on_error`** is typed as ``Callable[[Exception], None]``, matching the renderer (only `Exception` subclasses are passed through).
- **`Routes`:** duplicate route names are rejected at construction.
- **`@component`:** returning ``None`` or a non-``Element`` value raises a clear ``TypeError`` (including in ``render_to_tree(..., expand_components=True)``).
- **`streamtree.asyncio`:** task status dict updates are serialized with a lock; module and ``submit`` docstrings document rerun-polling semantics.
- **`Theme`:** ``primary_color`` is restricted to ``#RGB`` / ``#RRGGBB`` hex; ``font_stack`` rejects ``<``, ``>``, and backticks; ``custom_css`` rejects ``<script`` and ``expression(`` substrings (full ``custom_css`` remains trusted CSS).
- **`HStack`:** non-empty ``gap`` inserts gutter columns between children (CSS ``min-width`` on a spacer).

### Documentation

- README refresh (badges, absolute GitHub links for design docs and workflows); install examples pin **0.3.0**.
- Design docs live at `docs/PLAN.md`, `docs/ROADMAP.md`, and `docs/DEPENDENCY_STRATEGY.md` with updated cross-links.
- **StreamTree** is used as the product name in metadata and user-facing defaults (the PyPI / import name remains **`streamtree`**).

## [0.2.0] — 2026-05-12

### Added

- **Pydantic** and **typing-extensions** as core dependencies; stub optional extras (`tables`, `charts`, `ui`, `auth`, `asyncio`, `cli`, `all`) per dependency strategy.
- **`streamtree.app_context`**: `provider()` / `lookup()` / `current_bag()` for rerun-scoped DI-style values.
- **`streamtree.routing`**: `sync_route` / `set_route` for query-param + session alignment.
- **`Routes`** layout element (with Streamlit renderer) for one-of-many pages keyed by the active route.
- **`ErrorBoundary`** element with Streamlit renderer fallback and optional `on_error` callback.
- **`streamtree.forms`**: `str_field_names`, `model_validate_json`, `format_validation_errors` for Pydantic-first forms.
- Example **`examples/routed_app.py`**: multi-page navigation + JSON profile validation.

### Changed

- Stricter validation for routing params and route names, app-context keys, `Routes` defaults/query keys, and `Annotated[...]` handling in `str_field_names`; `current_bag()` returns a shallow copy.
- Pytest coverage targets `src/streamtree` by path to avoid import-order coverage warnings.

## [0.1.0] — 2026-05-11

### Added

- Initial public API: `@component`, `render`, virtual elements (`Page`, layouts, widgets).
- Session helpers: `state`, `toggle_state`, `form_state`, `session_state`, `memo`, `cache`.
- Streamlit renderer mapping the virtual tree to `st.*` calls (including `Form` and submit flows).
- `streamtree.testing.render_to_tree` for structure-focused tests without a live Streamlit session.
- Runnable example: `examples/counter.py`.
- Design docs under `docs/` (plan, roadmap, dependency strategy).

[0.10.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.10.0
[0.9.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.9.0
[0.8.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.8.0
[0.7.1]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.7.1
[0.7.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.7.0
[0.6.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.6.0
[0.5.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.5.0
[0.4.1]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.4.1
[0.4.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.4.0
[0.3.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.3.0
[0.2.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.2.0
[0.1.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.1.0
