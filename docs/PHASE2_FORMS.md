# Phase 2 — extended form layout (0.9.0+)

This note complements [PHASE2_PORTALS_AND_PREFETCH.md](./PHASE2_PORTALS_AND_PREFETCH.md) for **layout-first** Pydantic forms.

## Field types in `streamtree.forms_layout`

| Pydantic annotation (concept) | Widget | Binding helper |
|------------------------------|--------|------------------|
| `str` / `str \| None` | `TextInput` | `bind_str_fields` |
| `int` / `float` / optional numeric | `NumberInput` | `bind_numeric_fields` |
| `bool` / `bool \| None` | `Checkbox` | `bind_bool_fields` |

`model_field_grid` lays out named fields in **rows** of `Columns`; `build_model_from_bindings` merges **str**, **numeric**, and **bool** binding maps into a single `model_validate` call.

## `st.form` and batch submit

Streamlit runs the full script on each rerun. A **`Form`** element in StreamTree maps to `st.form`; widgets inside read **`StateVar`** / **`FormState`** on each rerun after submit.

**Batch validation:** call `build_model_from_bindings` (and friends) **inside** the submit handler (e.g. a `Button` `on_click` that reads current `StateVar` values), not inside the worker thread. Surface failures with `format_validation_errors` next to the form.

## Deferred (Phase 3)

Select boxes from **Enums**, **date** / **datetime**, file fields, and nested models are intentionally thin or out of scope here; add them when data-plane widgets and pins are defined.
