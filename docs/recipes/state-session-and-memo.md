# State, session & memo

## Goal

Pick the right tool among **`state()`**, **`toggle_state()`**, **`form_state()`**, **`memo()`**,
**`memo_subtree()`**, and **`cache()`** without fighting Streamlit’s rerun model.

## Core ideas

| API | Session key shape | Typical use |
|-----|-------------------|-------------|
| **`state(initial, key=None)`** | `streamtree.<render_path>.sN` or `streamtree.state.<key>` if you pass `key=` | Counters, selections owned by a subtree |
| **`toggle_state()`** | Same family as `state` | Boolean feature flags |
| **`form_state()`** | Bound to a `Form` + widget keys | Values committed on submit |
| **`memo(fn, key, deps=…)`** | `streamtree.memo.<key>` | Expensive pure computation keyed by deps |
| **`memo_subtree(logical_key, deps, factory)`** | Path + logical key + deps hash | Skip rebuilding a **heavy element subtree** when deps unchanged |
| **`cache()`** | `streamtree.cache.<key>` | Session-global memo (document before using) |

Anonymous **`state()`** slots get a **per-render-path** index so nested components do not
collide. Prefer an **explicit `key=`** when the same component is reused in lists or tabs.

## Explicit keys (recommended pattern)

```python
from streamtree import component, render
from streamtree.elements import Button, Page, Text
from streamtree.state import state


@component
def Row(item_id: str):
    qty = state(0, key=f"qty-{item_id}")
    return Text(f"{item_id}: {qty()}")


@component
def Cart():
    return Page(Row("a"), Row("b"), key="cart-page")
```

## `memo_subtree` sketch

Use when a subtree is expensive to **construct** (large lists, heavy Pydantic models) and
you can fingerprint inputs:

```python
from streamtree import component, render
from streamtree.elements import Page, VStack
from streamtree.state import memo_subtree


@component
def Heavy():
    def build():
        # Return elements; runs only when deps change for this render path + logical key.
        return VStack()

    return memo_subtree("heavy-panel", deps=("v1", "v2"), factory=build)


@component
def Root():
    return Page(Heavy(), key="root")


if __name__ == "__main__":
    render(Root())
```

Read the full playbook in [Performance](../PERFORMANCE.md) (large trees, `memo_subtree`,
`DeferredFragment`, URL-driven filters).

## Debugging keys in dev

- **`streamtree.debug_render_path`** — current render path string, or `None` outside `render()`.
- **`streamtree.testing.introspection.summarize_streamtree_session_state()`** — categories of
  StreamTree-owned `st.session_state` keys ([Testing & debugging](../TESTING_AND_DEBUG.md)).

## See also

- [Forms & validation](forms-and-validation.md) — `form_state` with `Form`
- [Routing & URLs](routing-and-urls.md) — drive `state` from query params
- [Examples](../EXAMPLES.md) — `model_form.py`, `counter.py`
