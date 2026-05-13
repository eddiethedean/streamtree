# Async & loading

## Goal

Run **stdlib-thread** work with **`streamtree.asyncio.submit`**, poll **`TaskHandle`** on
reruns, and map status to **`loading` / `ready` / `error`** subtrees with **`match_task`**
or **`match_task_many`**.

## Install

**`streamtree.asyncio`** ships in the default install (no extra). Keep **`[asyncio]`** as
metadata for future backends per [Dependency strategy](../DEPENDENCY_STRATEGY.md).

## Minimal submit + poll

Full small demo:

```python
--8<-- "examples/async_bg.py"
```

Run:

```bash
streamlit run examples/async_bg.py
```

## Declarative loading UI

Use **`streamtree.loading.match_task`** to pick which element subtree to show for each
**`TaskHandle.status`**. Multi-handle orchestration: **`match_task_many`**, stable ordering
with **`submit_many_ordered`** (see [Performance](../PERFORMANCE.md)).

```python
--8<-- "examples/async_loader_demo.py"
```

## Cancellation & cleanup

- **`TaskHandle.cancel()`** — cooperative cancel for running work; pair with
  **`is_task_cancel_requested`** / **`complete_cancelled`** in the worker.
- **`dismiss_task`** / **`dismiss_tasks`** — remove **terminal** session entries so a **`key`**
  can be reused without stale collisions.

## Dev inspection

**`streamtree.asyncio.summarize_async_tasks()`** returns JSON-serializable rows (status,
progress preview, cancel flags) for debugging panels or logs.

## See also

- [Portals & deferred UI](portals-and-deferred.md) — `DeferredFragment` for lower-priority regions
- [Phase 3 CRUD](../PHASE3_CRUD.md) — save intent + `submit` patterns
- [Examples](../EXAMPLES.md) — `async_ordered_loader_demo.py`, `deferred_region_demo.py`
