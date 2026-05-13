# Observability & ops

## Goal

Lightweight **counters**, **structured events**, and **session/task summaries** you can turn
on in staging without shipping a second observability stack.

## Perf counters

**`streamtree.perf`** exposes **`perf_bump`**, **`perf_snapshot`**, and
**`PERF_COUNTERS_KEY`** via **`app_context`**. Bump from hot paths; read snapshots in a
diagnostics component or sidebar.

## Enterprise-shaped events

**`streamtree.enterprise`** provides **`EventSink`**, **`emit_event`**, **`tenant_id`**,
**`redact_secrets`**—use when you need a stable hook for audit logs or downstream buses
without pinning a vendor ([Dependency strategy](../DEPENDENCY_STRATEGY.md)).

## Session + async introspection (dev)

At runtime (inside Streamlit):

```python
from streamtree import component, fragment
import streamlit as st
from streamtree.asyncio import summarize_async_tasks
from streamtree.testing.introspection import summarize_streamtree_session_state


@component
def DebugPanel():
    st.json({"session": summarize_streamtree_session_state(), "tasks": summarize_async_tasks()})
    return fragment()
```

Pair with **`debug_render_path`** to print the active render path during investigations.

## Static snapshots in CI

Use **`render_to_tree`** + **`summarize_tree_kinds`** (and **`streamtree tree --summarize`**
in pipelines) to catch accidental layout regressions without spinning browsers.

## See also

- [Testing & debugging](../TESTING_AND_DEBUG.md)
- [API reference](../reference/testing_api.md)
- [Async tasks reference](../reference/asyncio_api.md)
