# Data grids & charts

## Goal

Opt in to **AgGrid**, **Plotly**, **Altair**, and **Apache ECharts** behind StreamTree
elements so default installs stay light.

## Install extras

```bash
pip install "streamtree[tables]"   # DataGrid + pandas + streamlit-aggrid
pip install "streamtree[charts]"   # Chart, AltairChart, EChartsChart + pins
```

See [Dependency strategy](../DEPENDENCY_STRATEGY.md) for version policy.

## Tables

**`DataGrid`** wraps **`streamlit-aggrid`**. Full demo:

```python
--8<-- "examples/datagrid_demo.py"
```

Selection callbacks after render: **`examples/datagrid_selection_demo.py`** (same page on
[Examples](../EXAMPLES.md)).

## Charts

- **`Chart`** — Plotly via **`st.plotly_chart`**
- **`AltairChart`** — Altair via **`st.altair_chart`**
- **`EChartsChart`** — **`streamlit-echarts`**

Demos: `chart_demo.py`, `altair_chart_demo.py`, `echarts_demo.py`.

## Recipe: URL filter + grid

Pair [Routing & URLs](routing-and-urls.md) with **`sync_query_value`** so the grid’s query
or sort state survives reruns and sharing URLs. See [Performance](../PERFORMANCE.md) for
large-table guidance.

## See also

- [Phase 3 CRUD](../PHASE3_CRUD.md) — list/detail with **`DataGrid`**
- [Async & loading](async-and-loading.md) — fetch then render chart subtree
- [Examples](../EXAMPLES.md) — all data demos embedded
