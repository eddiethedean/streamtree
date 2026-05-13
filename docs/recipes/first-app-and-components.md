# First app & components

## Goal

Run a StreamTree app with a **`@component`**, **`state()`**, and **`render(Page(...))`**
so you have a mental model for every other recipe.

## Install

```bash
pip install streamlit streamtree
```

(`streamtree` pulls Pydantic and typing-extensions; see [Dependency strategy](../DEPENDENCY_STRATEGY.md).)

## Core ideas

1. **`@component`** marks a function whose body runs **on each Streamlit rerun** when the
   tree is rendered. It returns **elements** (layout + widgets), not HTML strings.
2. **`render(root)`** walks the tree and calls Streamlit primitives under the hood.
3. **`Page`** is a common top-level container; **`Card`**, **`VStack`**, **`Text`**, **`Button`**
   compose the visible UI.

## Minimal counter (full file)

The repository’s counter demo is the canonical “first app”. Full source:

```python
--8<-- "examples/counter.py"
```

Run from the repository root:

```bash
streamlit run examples/counter.py
```

## `streamtree tree` on the same tree

With **`pip install "streamtree[cli]"`** you can snapshot structure without running the UI:

```bash
streamtree tree examples.counter:streamtree_tree_root --summarize
```

See [Testing & debugging](../TESTING_AND_DEBUG.md) for JSON snapshots in pytest.

## Variations

- **Multiple components:** nest `Page(Header(), Body(), Footer())` where each child is a
  **`@component`** or plain elements.
- **Imperative Streamlit inside a component:** you may call `st.*` in the component body,
  then return **`fragment()`** if the subtree is entirely imperative (see README “Using
  Streamlit inside components”).
- **App shell later:** when you need `st.set_page_config` once, move to **`App`** +
  **`render_app`** ([App shell, theme & context](app-theme-context.md)).

## See also

- [State, session & memo](state-session-and-memo.md) — how `state(0, key="…")` maps to `st.session_state`
- [Layouts & error boundaries](layout-shells.md) — `Card`, `VStack`, `ErrorBoundary`
- [Examples (full source)](../EXAMPLES.md) — every demo script embedded
