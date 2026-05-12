# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.4.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.4.0
[0.3.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.3.0
[0.2.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.2.0
[0.1.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.1.0
