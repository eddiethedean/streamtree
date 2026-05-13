# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] — 2026-05-12

### Added

- **CLI (`[cli]`):** **`streamtree init`** scaffolds **`app.py`** and optional **`pages/`** (see **`streamtree.helpers.scaffold`**).
- **Auth (`[auth]`):** **`streamtree.auth.build_authenticator`**, **`AuthGate`** element (in **`streamtree.elements.auth_gate`**), and Streamlit renderer integration for **`streamlit-authenticator`**.
- **Overlays:** **`Dialog`** and **`Popover`** layout elements (``st.dialog`` / ``st.popover`` with fallbacks); **`streamlit>=1.33.0`** core floor.
- **UI extras (`[ui]`):** **`ColoredHeader`** and **`VerticalSpaceLines`** wrapping **`streamlit-extras`** (lazy import + install hint).
- **Examples:** **`examples/overlay_demo.py`**, **`examples/auth_demo.py`**.
- **Docs:** [`docs/PHASE2_TAIL.md`](docs/PHASE2_TAIL.md) for post-0.6.0 Phase 2 grooming.

### Changed

- **Dependencies:** **`streamlit>=1.33.0`**; **`[auth]`** pins **`streamlit-authenticator`**, **`[ui]`** pins **`streamlit-extras`**; **`[dev]`** includes both for contributor / CI installs.
- **`session_state(..., default=None)`:** first read on a missing key raises **`ValueError`** with a hint instead of a bare **`KeyError`**.
- **`streamtree.helpers.scaffold.app_py_source`:** embeds **`page_title`** via **`repr()`** so generated **`app.py`** stays valid for arbitrary titles.
- **`streamtree.asyncio`:** **`TaskHandle`** and **`set_task_progress`** only touch task dicts that include a real **`threading.Lock`** (same shape as **`submit`**); fake **`_submitted`** entries without a lock are replaced on **`submit`**.
- **`ErrorBoundary`:** if **`on_error`** raises, the error is logged and **`fallback`** is still rendered.

### Documentation

- README: **0.6.0** pin, Streamlit **1.33+**, **`streamtree init`**, auth / overlay / **`[ui]`** capabilities; releases tag **`v0.6.0`**; overlay bullet clarifies **`Dialog`** legacy (inline) vs **`Popover`** (expander) fallbacks.
- [ROADMAP.md](docs/ROADMAP.md), [PLAN.md](docs/PLAN.md), [DEPENDENCY_STRATEGY.md](docs/DEPENDENCY_STRATEGY.md): **0.6.0** shipped scope and optional-extra notes (including empty **`[all]`** placeholder).
- **`Dialog`**, **`App` / `apply_page_config`:** docstrings for legacy dialog behavior and one-shot **`st.set_page_config`** per session.

## [0.5.0] — 2026-05-12

### Added

- **`streamtree.helpers.pages`:** `PageEntry`, `pages_dir_next_to`, `list_page_entries`, and `discover_pages` for Streamlit `pages/` discovery (stdlib + pathlib); re-exported from **`streamtree.helpers`**.
- **`streamtree.asyncio`:** `set_task_progress` and **`TaskHandle.progress()`** for lock-safe, rerun-polled worker progress (task dict includes `progress`).
- **Example:** `examples/pages_helpers_demo.py` with `examples/pages/1_About_demo.py` stub page.
- **Tests:** expanded coverage for **`streamtree.helpers.pages`** (paths, unicode, ordering, symlinks) and **`streamtree.asyncio`** progress (poll while running, error path, main-thread updates).

### Documentation

- README: **0.5.0** install pin, capabilities for multipage helpers + async progress, example command; releases tag example **`v0.5.0`**.
- [ROADMAP.md](docs/ROADMAP.md): release index **0.5.0**; Phase 2 “Next” backlog adjusted.
- [PLAN.md](docs/PLAN.md): packaging timeline **0.5.0** bullet.
- [DEPENDENCY_STRATEGY.md](docs/DEPENDENCY_STRATEGY.md): asyncio progress note; **`helpers.pages`** + **`[pages]`** stub subsection.

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
- [DEPENDENCY_STRATEGY.md](docs/DEPENDENCY_STRATEGY.md): CLI / **`[pages]`** / **`[runner]`** notes.
- [ROADMAP.md](docs/ROADMAP.md): **0.4.0** release index; Phase 2 “Next” adjusted.

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

[0.6.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.6.0
[0.5.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.5.0
[0.4.1]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.4.1
[0.4.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.4.0
[0.3.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.3.0
[0.2.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.2.0
[0.1.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.1.0
