# Multipage navigation

## Goal

Use Streamlit’s **`pages/`** layout with StreamTree **`PageLink`** rows built from discovery
helpers instead of hand-maintaining paths.

## Install

**`streamtree.helpers.pages`** ships in the default install. Optional **`[pages]`** extra
remains reserved for future pinned deps ([Dependency strategy](../DEPENDENCY_STRATEGY.md)).

## Discover + link pattern

Full demo:

```python
--8<-- "examples/pages_helpers_demo.py"
```

Stub page script under `examples/pages/`:

```python
--8<-- "examples/pages/1_About_demo.py"
```

Run the multipage demo from repo root:

```bash
streamlit run examples/pages_helpers_demo.py
```

## CLI scaffold with pages

```bash
pip install "streamtree[cli]"
streamtree init ./myapp --with-pages --name "My app"
```

Generated **`app.py`** wires **`discover_pages`** + **`page_links`** into a sidebar shell
(see **`streamtree.helpers.scaffold`**).

## Advanced helpers

- **`iter_page_entries`**, **`prefetch_page_sources`** — optional `compile()` warm-up without
  importing page modules ([Performance](../PERFORMANCE.md)).
- **`page_links_sidebar_sections`**, **`multipage_sidebar_nav`** — sectioned sidebars for
  larger `pages/` trees.

## See also

- [Routing & URLs](routing-and-urls.md) — when you stay in one script with `Routes`
- [Examples](../EXAMPLES.md) — `numeric_nav_demo.py` for numeric `PageLink` ordering
- [CLI & scaffolding](cli-and-scaffolding.md)
