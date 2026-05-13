"""Lightweight table exploration helpers (optional pandas via ``[tables]``)."""

from __future__ import annotations

from typing import Any


def column_summary(rows: list[dict[str, Any]], *, max_columns: int = 64) -> dict[str, Any]:
    """Return JSON-friendly column stats for a list of row dicts (stdlib only).

    Keys are unioned across rows in first-seen order (capped at ``max_columns``).
    """
    if max_columns < 1:
        raise ValueError("max_columns must be >= 1")
    keys: list[str] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        for k in row:
            if k in seen:
                continue
            if len(keys) >= max_columns:
                break
            seen.add(k)
            keys.append(str(k))
        if len(keys) >= max_columns:
            break
    cols: dict[str, dict[str, Any]] = {}
    for k in keys:
        present = 0
        types: set[str] = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            if k in row:
                present += 1
                types.add(type(row[k]).__name__)
        cols[k] = {"non_null_rows": present, "types": sorted(types)}
    return {"row_count": len(rows), "columns": cols}


def dataframe_profile(df: Any) -> dict[str, Any]:
    """Return shape + ``column_summary`` for a pandas ``DataFrame`` (requires pandas).

    Raises ``ImportError`` if pandas is not installed.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            'dataframe_profile requires pandas. Install with: pip install "streamtree[tables]"'
        ) from exc

    if not isinstance(df, pd.DataFrame):
        raise TypeError("dataframe_profile expects a pandas.DataFrame")
    rows = df.head(5000).to_dict(orient="records")
    summary = column_summary(rows, max_columns=min(64, max(1, len(df.columns))))
    return {"shape": [int(df.shape[0]), int(df.shape[1])], **summary}


__all__ = ["column_summary", "dataframe_profile"]
