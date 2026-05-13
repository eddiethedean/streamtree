# App shell, theme & context

## Goal

Call **`st.set_page_config` exactly once**, compose **sidebar + body** as elements, and
optionally inject **theme CSS** + **shared context** (`app_context.provider`).

## `App` + `render_app`

Full demo:

```python
--8<-- "examples/app_shell.py"
```

Run:

```bash
streamlit run examples/app_shell.py
```

## Theme variables

Use **`Theme`**, **`ThemeRoot`**, **`theme()`**, **`theme_css()`** (see **`streamtree.theme`**).
Wrap subtrees that should pick up variables in **`ThemeRoot`**.

## Shared values without prop drilling

**`app_context.provider`** during render installs values readable via **`lookup`** /
**`streamtree.enterprise`** patterns (events, tenant id, redaction). Keep payloads **small**
and JSON-friendly when you log or emit events.

## Overlay elements

**`Dialog`** and **`Popover`** map to Streamlit **`st.dialog`** / **`st.popover`** when
available; see **`examples/overlay_demo.py`** on the [Examples](../EXAMPLES.md) page.

## See also

- [Layouts & error boundaries](layout-shells.md)
- [Authentication gate](authentication-gate.md) — `AuthGate` in the tree
- [Plan](../PLAN.md) — architecture narrative
