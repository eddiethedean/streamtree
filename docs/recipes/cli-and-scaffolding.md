# CLI & scaffolding

## Goal

Use the **`streamtree`** Typer CLI for **run**, **tree**, **doctor**, and **init** templates
without memorizing `python -m streamlit` flags.

## Install

```bash
pip install "streamtree[cli]"
```

## Commands

| Command | Purpose |
|---------|---------|
| **`streamtree run app.py …`** | Forwards argv to **`python -m streamlit run`** (exit code preserved). |
| **`streamtree preview` / `serve`** | Aliases of **`run`** (same forwarding). |
| **`streamtree doctor`** | Prints StreamTree, Streamlit, Python, Typer presence. **`--verbose`** adds runtime + introspection hints. |
| **`streamtree tree module:attr`** | Dumps **`render_to_tree`** JSON / text / Mermaid; **`--summarize`**, **`--expand-components`** (needs Streamlit runtime). |
| **`streamtree init [dir]`** | Writes **`app.py`**; **`--with-pages`**, **`--template` / `-t`**, **`--force`**, **`--name`**. |

## Scaffold templates

```bash
streamtree init ./crm --template crud --name "CRM" --with-pages
```

Templates: **`default`**, **`crud`**, **`explore`**, **`enterprise`** (see **`streamtree.helpers.scaffold`**).

## Operator notes

Markdown runbook shipped with examples:

```markdown
--8<-- "examples/streamtree_run_demo.md"
```

## See also

- [Testing & debugging](../TESTING_AND_DEBUG.md)
- [API reference: CLI helpers](../reference/cli_helpers.md)
- [First app & components](first-app-and-components.md)
