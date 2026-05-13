# Organizing large apps

## Goal

Keep Streamlit reruns predictable as the element tree grows: **component boundaries**,
**stable keys**, **memoized subtrees**, and **clear module layout**.

## File & module layout

| Layer | Responsibility |
|-------|------------------|
| **`app.py` / `pages/*.py`** | Entrypoints: build `App` or call `render(Page(…))` |
| **`components/`** | `@component` definitions grouped by domain (billing, settings, …) |
| **`trees/` or `shell.py`** | Compose `Page`, `Sidebar`, `Routes`, portals |
| **`state/` helpers** | Pure functions that map session/query to view models (optional) |

Avoid cyclic imports: elements should not import entry scripts.

## Key discipline

1. **Every** dynamic list item subtree should carry a stable **`key=`** on the outer element.
2. Prefer **explicit `state(..., key=...)`** when the same component appears in loops/tabs.
3. Use **`memo_subtree`** for expensive **element construction**, not for hiding Streamlit
   side effects.

## When to split components

Split when:

- Body exceeds ~80–120 lines **or** mixes unrelated concerns.
- You need isolated testing via **`render_to_tree`** on a subtree.
- You want a **`ErrorBoundary`** around a risky region without wrapping the whole page.

Keep **thin** `Page` composers and **fat** domain components.

## Multipage vs in-script routing

Document the team choice in README/internal docs. Mixing **`pages/`** primary nav with a
second parallel **`Routes`** model confuses analytics and deep links—pick one ([Roadmap](../ROADMAP.md)).

## See also

- [Performance](../PERFORMANCE.md)
- [Phase 2 tail](../PHASE2_TAIL.md)
- [Testing & debugging](../TESTING_AND_DEBUG.md)
- [Examples](../EXAMPLES.md) — `phase2_composite_demo.py`
