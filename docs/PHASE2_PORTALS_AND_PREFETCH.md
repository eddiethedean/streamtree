# Phase 2 design: portals, prefetch, form layout

This note locks semantics for **portals / layout targets**, **route prefetch**, and the **layout-aware form builder** so implementations stay consistent with Streamlit’s rerun model. It extends [PHASE2_TAIL.md](./PHASE2_TAIL.md).

## Portals and layout targets

**Constraint:** Streamlit exposes one real **`st.sidebar`**, one main script body, and overlays (`st.dialog`, `st.popover`, …). StreamTree cannot attach arbitrary subtrees to arbitrary DOM nodes like a web VDOM portal.

**MVP semantics:**

1. **`Portal(slot, child)`** — Declares content that must **not** render in place. During a **pre-walk** of the virtual tree (before any `st.*` calls), each `Portal` appends its `child` to a **per-slot list** (order preserved by depth-first discovery).
2. **`PortalMount(slot)`** — At its position in the tree, renders **all** children collected for `slot` (in order), then clears that slot’s queue for the remainder of this rerun so content is not duplicated if multiple mounts existed (first mount wins; document **one mount per slot**).
3. **`ComponentCall` nodes** — The gather pass does **not** execute `@component` bodies. Portals declared **inside** a component are only visible **after** expansion at render time; registering portals from deep components requires the component to return them in its public tree (same rerun). This matches Streamlit’s “tree is built each rerun” model.

**Alternative (shell-only) slots:** `App` already maps **`sidebar`** + **`body`** via [app.py](../src/streamtree/app.py). **`SplitView`** (narrow + main columns) addresses “second sidebar” UX without a second `st.sidebar`.

## Route prefetch

**Not supported:** Running another page script’s Streamlit entrypoint early, or navigating without a rerun.

**Supported (`prefetch_page_sources`):**

- **Syntax warm-up:** `compile()` on page source text (read from disk) to catch **syntax errors** before the user opens a page, without importing the module (avoids `__main__` side effects).
- **Optional:** Iterate entries lazily via **`iter_page_entries`** for large `pages/` trees without building a full list up front.

Background **thread** prefetch of file reads may be composed with **`streamtree.asyncio.submit`**; results still only affect UI on the **next** rerun after you write session state or a cache.

## Layout-aware form builder

**Scope:** Pydantic models already work with **`bind_str_fields`**, **`bind_numeric_fields`**, **`str_text_inputs`**, **`number_inputs`** ([forms.py](../src/streamtree/forms.py)). The layout builder adds:

- **`model_field_grid`** — Arrange named fields into **rows** of **`Columns`** (each row is one `st.columns` strip) so labels/inputs follow a 2D grid instead of a single column.
- **`build_model_from_bindings`** — Read current `StateVar` values, run **`model_validate`**, surface **`ValidationError`** via existing **`format_validation_errors`**.

**Out of scope for this slice:** Generic non-Pydantic form state, multi-step wizards, and cross-page form persistence.

## Imperative handles

Streamlit does not expose stable focus/scroll APIs for arbitrary widgets across reruns. StreamTree documents **query params**, **`st.session_state`**, and **`st.rerun`** as the portable “imperative edge”; see README “Imperative handles” after this phase.

Extended field types and **`Form`** batch notes live in [PHASE2_FORMS.md](./PHASE2_FORMS.md).
