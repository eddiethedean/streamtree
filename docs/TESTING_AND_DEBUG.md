# Testing and debugging

StreamTree ships two complementary approaches: **static tree snapshots** (no Streamlit
session) and **runtime introspection** (inside `streamlit run`).

Broader step-by-step patterns (CLI, async, routing, CRUD, etc.) live under **[Recipes](recipes/README.md)**.

## Static structure: `render_to_tree`

Use `streamtree.testing.render_to_tree` in unit tests to assert layout and widget kinds
without executing Streamlit. Pair with `summarize_tree_kinds` for compact assertions.
See the [Testing API](reference/testing_api.md) reference page.

## CLI: `streamtree tree`

With `pip install "streamtree[cli]"`, print JSON, text, or Mermaid views:

```bash
streamtree tree mypkg.trees:build_root --format text
streamtree tree mypkg.trees:build_root --summarize
```

The target must be `module:attribute` where `attribute` is an `Element` or a zero-argument
callable returning one. From the repository root, `examples.counter:streamtree_tree_root`
works once the `examples` package is importable (see `examples/__init__.py`).

`--expand-components` expands `@component` bodies and **requires** an active Streamlit
runtime (for example inside `streamlit run`). Outside Streamlit, the CLI exits with an
error.

## Runtime: session keys and async tasks

Inside a running app:

- `streamtree.testing.introspection.summarize_streamtree_session_state` lists StreamTree-owned
  `st.session_state` keys with coarse categories ([Introspection API](reference/introspection_api.md)).
- `streamtree.asyncio.summarize_async_tasks` summarizes managed background task slots
  ([Async summaries](reference/asyncio_api.md)).

## Render path helper

`streamtree.debug_render_path` returns the active render-context path string, or `None`
outside `render()` / `render_app()`. See [Core API](reference/core_api.md).

## AppTest integration

`streamtree.testing.apptest.run_app_function` wraps `AppTest.from_function(...).run(...)`
for scripts that call `render` / `render_app` ([AppTest helper](reference/apptest_api.md)).
Use it when you need Streamlit widget queries; use `render_to_tree` when you only need
structure. Components that call `state()` need reruns like a real browser session; see
`tests/test_streamlit_app.py` for a broad renderer smoke test.
