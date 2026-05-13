# Forms & validation

## Goal

Collect user input with **StreamTree `Form`** + **`form_state`**, and optionally bind a
**Pydantic** model with **`streamtree.forms`** helpers.

## Install

Default `streamtree` includes Pydantic v2. Optional layout helpers live in
**`streamtree.forms_layout`** (see [Phase 2 form layout](../PHASE2_FORMS.md)).

## Pattern A — `form_state` + widgets

Use when you want **commit-on-submit** semantics (values update after `st.form_submit_button`).

Conceptual shape:

```python
from streamtree import component, render
from streamtree.elements import Form, Page, TextInput
from streamtree.state import form_state


@component
def Editor():
    title = form_state("", key="title_field")
    return Form(
        TextInput("Title", value=title),
        # ... submit button inside Form in real apps; see examples/model_form.py
        form_key="editor",
    )


@component
def Root():
    return Page(Editor(), key="page")
```

## Pattern B — Pydantic bindings

**`bind_str_fields`**, **`bind_numeric_fields`**, **`bind_bool_fields`** pair model fields
with `StateVar`s so you can render **`str_text_inputs`**, **`number_inputs`**, etc., from a
schema. See **`streamtree.forms`** module docstrings and [Phase 2 form layout](../PHASE2_FORMS.md)
for **`model_field_grid`** and **`build_model_from_bindings`**.

## Validation workflow

1. Keep **raw** values in `form_state` / bound state vars while editing.
2. On submit, call **`model_validate_json`** or Pydantic **`model_validate`** on a dict you build.
3. Surface errors with **`format_validation_errors`** (`streamtree.forms`) into `Markdown`
   or `Text` elements.

## Full runnable reference

```python
--8<-- "examples/model_form.py"
```

Run:

```bash
streamlit run examples/model_form.py
```

## See also

- [Phase 2 form layout](../PHASE2_FORMS.md) — grids, bool fields, `build_model_from_bindings`
- [Phase 3 CRUD](../PHASE3_CRUD.md) — save intent + URL id patterns
- [Layouts & error boundaries](layout-shells.md) — wrapping forms in `Card` / `ErrorBoundary`
