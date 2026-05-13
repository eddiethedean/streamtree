"""Tests for optional ``[tables]`` / ``[charts]`` rendering."""

from __future__ import annotations

import builtins
from unittest.mock import MagicMock, patch

import pytest

from streamtree.charts import (
    AltairChart,
    Chart,
    EChartsChart,
    render_altair_chart,
    render_chart,
    render_echarts_chart,
)
from streamtree.tables import DataGrid, render_datagrid


@patch("st_aggrid.AgGrid")
def test_render_datagrid_on_result_called_with_aggrid_return(mock_aggrid: MagicMock) -> None:
    sentinel = object()
    mock_aggrid.return_value = sentinel
    called: list[object] = []

    def cb(r: object) -> None:
        called.append(r)

    render_datagrid(
        DataGrid([{"a": 1}], on_result=cb, key="gk"),
        widget_key="widget-key",
    )
    assert called == [sentinel]


@patch("st_aggrid.AgGrid")
def test_render_datagrid_skips_on_result_when_aggrid_raises(mock_aggrid: MagicMock) -> None:
    mock_aggrid.side_effect = RuntimeError("grid failed")
    called: list[object] = []

    def cb(r: object) -> None:
        called.append(r)

    with pytest.raises(RuntimeError, match="grid failed"):
        render_datagrid(DataGrid([{"a": 1}], on_result=cb), widget_key="w")
    assert called == []


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


@patch("streamtree.echarts_chart._st_echarts_call")
def test_render_echarts_chart_delegates(mock_st_echarts: MagicMock) -> None:
    options = {"series": [{"type": "bar", "data": [1, 2]}]}
    render_echarts_chart(EChartsChart(options, height=240, key="ek"), widget_key="wk")
    mock_st_echarts.assert_called_once_with(
        options=dict(options),
        height="240px",
        key="wk",
    )


@patch("streamtree.echarts_chart._st_echarts_call")
def test_render_echarts_chart_height_str_passthrough(mock_st_echarts: MagicMock) -> None:
    options = {"series": []}
    render_echarts_chart(EChartsChart(options, height="400px"), widget_key="k2")
    mock_st_echarts.assert_called_once_with(
        options=dict(options),
        height="400px",
        key="k2",
    )


@patch("streamtree.echarts_chart._st_echarts_call")
def test_render_echarts_chart_default_height_when_none(mock_st_echarts: MagicMock) -> None:
    options = {"series": []}
    render_echarts_chart(EChartsChart(options), widget_key="k3")
    mock_st_echarts.assert_called_once_with(
        options=dict(options),
        height="300px",
        key="k3",
    )


def test_render_echarts_chart_missing_dep_raises() -> None:
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "streamlit_echarts" or name.startswith("streamlit_echarts."):
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=_fake):
        with pytest.raises(ImportError, match=r"streamtree\[charts\]"):
            render_echarts_chart(EChartsChart({}), widget_key="k")


@patch("streamtree.charts.st")
def test_render_altair_chart_delegates(mock_st: MagicMock) -> None:
    spec = object()
    render_altair_chart(AltairChart(spec, use_container_width=False), widget_key="ak")
    mock_st.altair_chart.assert_called_once_with(spec, use_container_width=False, key="ak")


def test_render_altair_chart_missing_altair_raises() -> None:
    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "altair":
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=_fake):
        with pytest.raises(ImportError, match=r"streamtree\[charts\]"):
            render_altair_chart(AltairChart(MagicMock()), widget_key="k")

    real_import = builtins.__import__

    def _fake(name: str, *a: object, **kw: object):
        if name == "plotly":
            raise ImportError("blocked")
        return real_import(name, *a, **kw)

    with patch.object(builtins, "__import__", side_effect=_fake):
        with pytest.raises(ImportError, match=r"streamtree\[charts\]"):
            render_chart(Chart(MagicMock()), widget_key="k")
