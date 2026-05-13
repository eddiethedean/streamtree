"""Tests for ``streamtree.helpers.explore``."""

from __future__ import annotations

import builtins

import pytest

from streamtree.helpers.explore import column_summary, dataframe_profile


def test_column_summary_basic() -> None:
    rows = [{"a": 1, "b": "x"}, {"a": 2, "b": None}]
    out = column_summary(rows)
    assert out["row_count"] == 2
    assert "a" in out["columns"] and "b" in out["columns"]


def test_column_summary_max_columns() -> None:
    rows = [{str(i): i for i in range(3)}]
    out = column_summary(rows, max_columns=2)
    assert len(out["columns"]) == 2


def test_column_summary_max_columns_invalid() -> None:
    with pytest.raises(ValueError, match="max_columns"):
        column_summary([], max_columns=0)


def test_column_summary_skips_non_dict_rows() -> None:
    out = column_summary([{"a": 1}, "skip", {"b": 2}])
    assert out["row_count"] == 3
    assert set(out["columns"]) == {"a", "b"}


class _DupKeyDict(dict):
    """``for k in row`` yields duplicate keys (exercises duplicate-key guard)."""

    def __iter__(self):
        yield from ("a", "a", "b")


def test_column_summary_duplicate_key_iterations() -> None:
    out = column_summary([_DupKeyDict(a=1, b=2)])
    assert set(out["columns"]) == {"a", "b"}


def test_dataframe_profile_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    real = builtins.__import__

    def fake(name: str, *a: object, **kw: object):
        if name == "pandas":
            raise ImportError("blocked")
        return real(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake)
    with pytest.raises(ImportError, match="dataframe_profile requires pandas"):
        dataframe_profile(object())


def test_dataframe_profile_with_pandas() -> None:
    pd = pytest.importorskip("pandas")
    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    prof = dataframe_profile(df)
    assert prof["shape"] == [2, 2]
    assert "columns" in prof


def test_dataframe_profile_rejects_non_dataframe() -> None:
    pd = pytest.importorskip("pandas")
    with pytest.raises(TypeError, match="DataFrame"):
        dataframe_profile(pd.Series([1, 2]))
