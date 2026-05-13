# Streamlit interop

## Goal

Mix **imperative `st.*` calls** with StreamTree elements in the same **`@component`** body
without breaking the tree model.

## Rules of thumb

1. **Stable `key=`** on imperative Streamlit widgets whenever Streamlit requires keys across
   reruns.
2. If a subtree is **only** imperative Streamlit (no StreamTree elements returned), return
   **`fragment()`** so the renderer does not expect child elements there.
3. Prefer StreamTree **elements** for layout you want in **`render_to_tree`** snapshots—
   imperative sections appear as gaps unless you wrap them thoughtfully.

## Minimal pattern

```python
from streamtree import component, render
from streamtree.core.element import fragment
from streamtree.elements import Page, Text
import streamlit as st


@component
def Mixed():
    st.metric("Rows", 42)
    return fragment(Text("Also from StreamTree"))


@component
def Root():
    return Page(Mixed(), key="page")


if __name__ == "__main__":
    render(Root())
```

## See also

- Root [README on GitHub](https://github.com/streamtree-dev/streamtree/blob/main/README.md) — “Using Streamlit inside components”
- [First app & components](first-app-and-components.md)
- [Layouts & error boundaries](layout-shells.md)
