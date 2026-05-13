# Layouts & error boundaries

## Goal

Structure pages with **`VStack`**, **`HStack`**, **`Grid`**, **`Columns`**, **`Tabs`**,
**`Card`**, **`Sidebar`**, **`Form`**, and contain failures with **`ErrorBoundary`**.

## Layout primitives

| Element | When to use |
|---------|-------------|
| **`VStack` / `HStack`** | Vertical/horizontal sequences; `HStack` supports `gap=` |
| **`Grid` / `Columns`** | Responsive columns; `Grid` takes `columns=` count |
| **`Tabs`** | Pair `(title, child)` entries; each child is its own subtree |
| **`Card`** | Group related controls with a simple frame |
| **`Sidebar`** | Shell sidebar region when not using Streamlit multipage-only layouts |
| **`Form`** | Widgets that share submit semantics (`form_key=`) |
| **`Spacer` / `Divider` / `Title` / `Subheader` / `Markdown`** | Typography and rhythm |

## Error boundaries

Wrap risky subtrees:

```python
from streamtree import component
from streamtree.elements import ErrorBoundary, Markdown, Text, VStack


@component
def RiskyChartRegion():
    return Text("replace with chart subtree")


@component
def SafeDashboard():
    return ErrorBoundary(
        child=RiskyChartRegion(),
        fallback=VStack(Text("Chart unavailable"), Markdown("Try again later.")),
        on_error=None,  # optional logger
    )
```

On failure the renderer logs and draws **`fallback`** (see renderer tests for coverage).

## Composite example

The Phase 2 composite demo combines **`Routes`**, **`ErrorBoundary`**, **`app_context`**, and
**`submit_many`**:

```python
--8<-- "examples/phase2_composite_demo.py"
```

## See also

- [Phase 2 portals & prefetch](../PHASE2_PORTALS_AND_PREFETCH.md)
- [Phase 2 form layout](../PHASE2_FORMS.md) — grid forms
- [Examples](../EXAMPLES.md) — `phase2_layout_demo.py`
