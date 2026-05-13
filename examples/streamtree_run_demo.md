# Running StreamTree examples with the optional CLI

Install Typer via the **`[cli]`** extra (see `pyproject.toml`):

```bash
pip install "streamtree[cli]"
```

The **`streamtree`** script delegates to Streamlit’s own CLI:

```bash
streamtree run examples/counter.py
streamtree run examples/numeric_nav_demo.py -- --server.headless true
streamtree run examples/pages_helpers_demo.py
```

Arguments after the script path are forwarded unchanged to `python -m streamlit run …`. The working directory and exit code are those of the child process.

For support or bug reports, run:

```bash
streamtree doctor
```

This prints **streamtree**, **streamlit**, and **Python** versions, and whether **Typer** is importable.

## Scaffolding a new app (`streamtree init`)

Generate **`app.py`** (and optionally **`pages/`**) in the current directory or under a target path:

```bash
mkdir myapp && cd myapp
streamtree init --with-pages
streamtree run app.py
```

Or pass a directory explicitly:

```bash
streamtree init myapp
```

Use **`--force`** to overwrite existing generated files. **`--name`** sets the **`App.page_title`** string in the template.

**Templates (0.10.0+):** **`--template`** (short **`-t`**) selects the generated **`app.py`** body:

| Value | Purpose |
|-------|---------|
| **`default`** | Current multipage-aware shell (same as omitting **`--template`**) |
| **`crud`** | **`Routes`** + **`streamtree.crud.save_intent_counter`** starter |
| **`explore`** | **`column_summary`** on in-memory rows + Markdown preview |
| **`enterprise`** | **`app_context.provider`** + **`streamtree.enterprise`** event sink stub |

Examples:

```bash
streamtree init myapp --template crud --name "My CRUD"
streamtree init myapp -t explore
streamtree init myapp --template enterprise --force
```

The always-supported path remains:

```bash
streamlit run examples/counter.py
streamlit run examples/pages_helpers_demo.py
```
