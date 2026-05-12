# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] — 2026-05-12

### Added

- **`streamtree.app.App`** shell with optional sidebar composition, **`apply_page_config`**, **`app_root_element`**, and **`render_app()`** (one-time `st.set_page_config` guard).
- **`streamtree.theme`**: **`Theme`** (Pydantic), **`theme()`** / **`theme_css()`**, and **`ThemeRoot`** element for CSS injection via `app_context.provider(theme=...)`.
- **`streamtree.asyncio`**: **`submit()`** / **`TaskHandle`** for daemon-thread background work with session-scoped poll keys (stdlib-only; optional `[asyncio]` extra unchanged as meta).
- **`streamtree.forms`**: **`bind_str_fields`** and **`str_text_inputs`** for declarative `TextInput` grids from Pydantic string fields.
- Examples **`examples/app_shell.py`**, **`examples/async_bg.py`**, **`examples/model_form.py`**.

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

[0.3.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.3.0
[0.2.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.2.0
[0.1.0]: https://github.com/streamtree-dev/streamtree/releases/tag/v0.1.0
