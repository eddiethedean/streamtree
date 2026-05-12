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

The always-supported path remains:

```bash
streamlit run examples/counter.py
streamlit run examples/pages_helpers_demo.py
```
