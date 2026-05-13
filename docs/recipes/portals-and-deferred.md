# Portals & deferred UI

## Goal

Render into **named slots** (`Portal` / `PortalMount`), split narrow/main columns with
**`SplitView`**, and mark **lower-priority** subtrees with **`DeferredFragment`** when
Streamlit exposes **`st.fragment`**.

## Portals

Read the contract in [Phase 2 portals & prefetch](../PHASE2_PORTALS_AND_PREFETCH.md).
Portals let you **gather** children in one pass and **mount** them elsewhere in the shell
(sidebar, dialog targets, etc.) while keeping a single StreamTree tree.

## Deferred fragments

**`DeferredFragment`** wraps children in **`st.fragment`** when available so reruns can
isolate expensive regions. Demo:

```python
--8<-- "examples/deferred_region_demo.py"
```

## Composite layout stress test

`phase2_composite_demo.py` mixes **`Routes`**, **`ErrorBoundary`**, **`submit_many`**, and
shell-friendly structure—use it as a “kitchen sink” reference when learning portals-adjacent
patterns.

## See also

- [Async & loading](async-and-loading.md)
- [Performance](../PERFORMANCE.md) — large-tree + fragment guidance
- [Examples](../EXAMPLES.md)
