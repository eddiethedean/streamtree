# Routing & URLs

## Goal

Switch UI **inside one Streamlit script** using **`Routes`** and/or keep session aligned
with **query parameters** (`sync_query_value`, `set_query_value`, clears).

## Pick one primary navigation model

Streamlit’s native **`pages/`** directory is a **separate entrypoint per page**. **`Routes`**
switches subtrees **within one script** using query params. Mixing both as “primary” nav
without discipline confuses users—pick one model per product (see [Roadmap](../ROADMAP.md)).

## In-script routing with `Routes`

Full demo:

```python
--8<-- "examples/routed_app.py"
```

Run:

```bash
streamlit run examples/routed_app.py
```

## Query string filters

Use **`streamtree.routing.sync_query_value`** / **`set_query_value`** when a string param
should both appear in the URL and live in `session_state`. Batch updates and clears are
in **`update_query_params`**, **`clear_query_param`**, **`clear_route`** (see README and
`streamtree.routing` docstrings).

## Recipe: deep-link a detail id

1. Store **`selected_id_from_query`** (or a thin wrapper) from **`streamtree.crud`** when
   you follow [Phase 3 CRUD](../PHASE3_CRUD.md).
2. Render **list** vs **detail** subtree based on id presence.
3. Bump a **save-intent counter** on “Save” so async work keys stay unique across logical saves.

## See also

- [Multipage navigation](multipage-navigation.md) — `pages/` helpers
- [Async & loading](async-and-loading.md) — URL-driven fetch patterns
- [Examples](../EXAMPLES.md) — `routed_app.py`, CRUD demos
