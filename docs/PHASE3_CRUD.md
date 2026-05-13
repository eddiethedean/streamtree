# Phase 3 — CRUD and data-heavy patterns

This note complements [`PERFORMANCE.md`](./PERFORMANCE.md) with **repeatable shapes** for list/detail/edit flows on Streamlit’s rerun model. It is **not** a full admin framework: stay with explicit `state`, elements, and optional extras.

## Building blocks

| Concern | StreamTree pieces |
|--------|-------------------|
| Tabular data | **`DataGrid`** (`[tables]` extra) or **`DataFrame`** for simple tables |
| Filters in the URL | **`routing.sync_query_value`** / **`set_query_value`** (see PERFORMANCE) |
| Forms | **`Form`**, **`TextInput`**, **`streamtree.forms`**, **`streamtree.forms_layout`** |
| Async save/load | **`streamtree.asyncio.submit`** / **`submit_many`** + **`TaskHandle`** |
| Declarative branches | **`streamtree.loading.match_task`**; parallel waits → **`match_task_many`** |
| Failure isolation | **`ErrorBoundary`** around risky subtrees |

## Recommended flow

1. **List** — Hold rows in **`state(..., key=...)`** (or load via `submit` and `match_task`). For rich grids, bind **`DataGrid`** selection to session state keys `streamlit-aggrid` exposes (or use **`DataGrid.on_result`** to observe the **`AgGrid`** return value in the same run), then mirror into a **`StateVar`** in your `@component` on the next rerun.
2. **Selection** — Keep **`selected_id`** (or similar) in **`state`**. Row actions use **`Button.on_click`** or grid callbacks to update selection and seed edit fields.
3. **Edit** — Use **`Form`** + **`TextInput(value=state_var)`** so submit batches match Streamlit’s form semantics.
4. **Save** — Start **`submit(save_fn, key="...")`** from the render path when the user intent is clear (for example after a “Save” click sets a **`save_version`** counter you read on the next rerun). Use **`match_task`** (or **`match_task_many`** if several keys must finish together) to swap loading / success / error UI.
5. **Cleanup** — After a terminal task, call **`dismiss_task`** / **`dismiss_tasks`** before reusing the same `key` for a new logical job (see PERFORMANCE and `streamtree.asyncio` docstring).

## Example

[`examples/crud_pattern_demo.py`](https://github.com/streamtree-dev/streamtree/blob/main/examples/crud_pattern_demo.py) shows in-memory list/edit/add plus **`match_task_many`** over two parallel **`submit`** handles (stand-ins for reference data). Swap the bodies for real I/O as needed.

## Charts and reporting

Optional **`[charts]`** provides **`Chart`** (Plotly), **`AltairChart`** (Altair), and **`EChartsChart`** (Apache ECharts / **`streamlit-echarts`**). Prefer small, composable chart elements next to tables rather than oversized single-page dashboards unless you add **`fragment()`** or portal-based shells for layout control. **`DataGrid.on_result`** (same-run hook after **`AgGrid`**) can mirror grid return values into **`state()`** on the next interaction-driven rerun.
