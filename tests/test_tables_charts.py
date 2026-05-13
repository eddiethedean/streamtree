"""Tests for optional ``[tables]`` / ``[charts]`` rendering."""

from __future__ import annotations

import builtins
from unittest.mock import MagicMock, patch

import pytest

from streamtree.charts import Chart, render_chart
from streamtree.tables import DataGrid, render_datagrid


@patch("st_aggrid.AgGrid")
def test_render_datagrid_forwards_options(mock_aggrid: MagicMock) -> None:
    el = DataGrid(
        [{"a": 1, "b": 2}],
        height=222,
        editable=True,
        selection_mode="single",
        grid_options={"rowHeight": 44, "defaultColDef": {"sortable": False}},
        key="gk",
    )
    render_datagrid(el, widget_key="widget-key")
    mock_aggrid.assert_called_once()
    kw = mock_aggrid.call_args.kwargs
    assert kw["height"] == 222
    assert kw["key"] == "widget-key"
    go = kw["gridOptions"]
    assert go["rowHeight"] == 44
    assert go["defaultColDef"]["editable"] is True
    assert go["defaultColDef"]["sortable"] is False
    assert go["rowSelection"] == "single"


@patch("st_aggrid.AgGrid")
def test_render_datagrid_multiple_selection_sets_row_selection(mock_aggrid: MagicMock) -> None:
    el = DataGrid([{"a": 1}], selection_mode="multiple")
    render_datagrid(el, widget_key="w")
    go = mock_aggrid.call_args.kwargs["gridOptions"]
    assert go["rowSelection"] == "multiple"


@patch("st_aggrid.AgGrid")
def test_render_datagrid_passes_through_dataframe(mock_aggrid: MagicMock) -> None:
    import pandas as pd

    df = pd.DataFrame({"z": [3]})
    render_datagrid(DataGrid(df), widget_key="w2")
    assert mock_aggrid.call_args.kwargs["data"] is df


@patch("streamtree.charts.st")
def test_render_chart_delegates(mock_st: MagicMock) -> None:
    fig = object()
    render_chart(Chart(fig, use_container_width=False), widget_key="ck")
    mock_st.plotly_chart.assert_called_once_with(fig, use_container_width=False, key="ck")


def test_render_datagrid_missing_aggrid_raises() -> None:
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "st_aggrid" or name.startswith("st_aggrid."):
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=_fake):
        with pytest.raises(ImportError, match=r"streamtree\[tables\]"):
            render_datagrid(DataGrid([{"x": 1}]), widget_key="k")


def test_render_chart_missing_plotly_raises() -> None:
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "plotly":
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=_fake):
        with pytest.raises(ImportError, match=r"streamtree\[charts\]"):
            render_chart(Chart(MagicMock()), widget_key="k")
