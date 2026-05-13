# List / detail / save (CRUD-shaped flows)

## Goal

Ship **list → detail → save** flows with **`DataGrid`**, URL **`id`**, **`save_intent_counter`**,
and **`match_task_many`** without adopting a heavyweight admin framework.

## Read the pattern doc first

[Phase 3 CRUD patterns](../PHASE3_CRUD.md) is the authoritative narrative. This recipe only
orients you to the moving parts.

## Moving parts

1. **`selected_id_from_query`** — keep the selected row’s id in the URL for deep links.
2. **`save_intent_counter`** — monotonic counter so each save starts **fresh async work**
   under a new logical key.
3. **`match_task_many`** — declarative UI for **all handles done**, **any error**, or
   **any cancelled** when several **`submit`** calls are in flight.

## Full demos (embedded)

**Pattern demo** (in-memory list + parallel reference fetches):

```python
--8<-- "examples/crud_pattern_demo.py"
```

**Automation demo** (CRUD helpers beside normal `state`):

```python
--8<-- "examples/crud_automation_demo.py"
```

## CLI shell

```bash
streamtree init ./myapp --template crud --name "My app"
```

## See also

- [Data grids & charts](data-grids-and-charts.md)
- [Async & loading](async-and-loading.md)
- [Routing & URLs](routing-and-urls.md)
