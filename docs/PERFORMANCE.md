# Performance and data-heavy Streamlit apps

StreamTree stays on Streamlit’s **sync, rerun-driven** model. This note lists practical
patterns for heavier work without blocking the script longer than necessary.

## Session helpers

- **`memo`** / **`cache`** in `streamtree.state` — reuse derived values across reruns
  with stable keys; prefer scoping keys via the render path or explicit `key=` when
  the value is global to a subtree.
- **`st.cache_data`** — safe for pure (or clearly keyed) data loads; call from inside
  `@component` bodies when the dependency inputs are stable across reruns.

## Imperative subtrees

Use **`fragment()`** when a branch is drawn entirely with `st.*` and does not need
virtual elements, so StreamTree does not wrap it unnecessarily.

## Background work

Use **`streamtree.asyncio.submit`** / **`submit_many`** for thread offload; poll
**`TaskHandle.status`** (and **`progress()`**) on reruns. For declarative trees, use
**`streamtree.loading.match_task`** to map status to `loading` / `ready` / `error`
elements (see `examples/async_loader_demo.py`). For **several** parallel handles (for example
after **`submit_many`**), use **`streamtree.loading.match_task_many`**: it shows **`loading`**
until **all** are **`done`**, **`error`** if **any** failed, **`cancelled`** (or **`error`**) if
**any** cancelled, and then **`ready(tuple of results))`**.

After a terminal **done** / **error** / **cancelled** run, **`streamtree.asyncio.dismiss_task`**
drops the session slot for a ``key`` so the next **`submit`** can reuse that key safely
(do not call while the task is still **running**). **0.9.0+** **`dismiss_tasks`** applies
the same rules across several keys and returns how many slots were cleared.

## URL filter state

**`streamtree.routing.sync_query_value`** / **`set_query_value`** mirror arbitrary
query params into session (similar to **`sync_route`** but with empty-string defaults
allowed). Pair with **`state()`** for values you do not want in the URL. **0.9.0+**
adds **`update_query_params`** (multi-key), **`clear_query_param`**, and **`clear_route`**
for imperative URL hygiene (still rerun-driven; see README “Imperative handles”).

## Multipage prefetch (0.9.0+)

Use **`streamtree.helpers.iter_page_entries`** for lazy iteration and
**`streamtree.helpers.prefetch_page_sources`** to **`compile()`** page script text
without importing modules (catches syntax errors early). This does **not** run
another page’s Streamlit script ahead of time; UI still advances on reruns. See
**`docs/PHASE2_PORTALS_AND_PREFETCH.md`**. For **sectioned sidebar** links built from the
same discovery data, use **`page_links_sidebar_sections`** / **`multipage_sidebar_nav`** (0.9.0+).

## Optional data extras

- **`pip install "streamtree[tables]"`** — **`DataGrid`** (streamlit-aggrid).
- **`pip install "streamtree[charts]"`** — **`Chart`** (Plotly) and **`AltairChart`** (Altair via `st.altair_chart`).

Keep expensive third-party imports inside render paths or optional modules so
`pip install streamtree` stays lean.
