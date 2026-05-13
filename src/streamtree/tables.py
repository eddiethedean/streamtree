"""Rich interactive grids behind ``pip install \"streamtree[tables]\"`` (``streamlit-aggrid``)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from streamtree.core.element import Element


@dataclass(frozen=True)
class DataGrid(Element):
    """Declarative wrapper around ``st_aggrid.AgGrid`` (install the ``[tables]`` extra).

    Optional ``on_result`` runs in the same Streamlit script rerun immediately after a
    successful ``AgGrid`` call; keep handlers fast and idempotent, and offload heavy work
    to ``asyncio.submit`` + ``match_task`` (see :func:`render_datagrid`).
    """

    data: Any = None
    height: int = 400
    editable: bool = False
    selection_mode: Literal["none", "single", "multiple"] = "none"
    grid_options: dict[str, Any] | None = None
    on_result: Callable[[Any], None] | None = None

    def __init__(
        self,
        data: Any,
        *,
        height: int = 400,
        editable: bool = False,
        selection_mode: Literal["none", "single", "multiple"] = "none",
        grid_options: dict[str, Any] | None = None,
        on_result: Callable[[Any], None] | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "height", height)
        object.__setattr__(self, "editable", editable)
        object.__setattr__(self, "selection_mode", selection_mode)
        object.__setattr__(self, "grid_options", grid_options)
        object.__setattr__(self, "on_result", on_result)


def _merge_grid_options(el: DataGrid) -> dict[str, Any]:
    opts = dict(el.grid_options or {})
    default_col = dict(opts.pop("defaultColDef", {}))
    if el.editable:
        default_col.setdefault("editable", True)
    if default_col:
        opts["defaultColDef"] = default_col
    if el.selection_mode == "single":
        opts.setdefault("rowSelection", "single")
    elif el.selection_mode == "multiple":
        opts.setdefault("rowSelection", "multiple")
    return opts


def _coerce_dataframe(data: Any) -> Any:
    import pandas as pd

    if isinstance(data, pd.DataFrame):
        return data
    return pd.DataFrame(data)


def render_datagrid(el: DataGrid, *, widget_key: str) -> None:
    """Render ``DataGrid`` using ``st_aggrid`` (raises if the optional extra is missing).

    When ``el.on_result`` is set, it is invoked once per successful ``AgGrid`` call with
    the return value (selection / grid state), still during the same Streamlit script run.
    Handlers should be fast and idempotent where possible; if ``AgGrid`` raises,
    ``on_result`` is not called. Prefer ``asyncio.submit`` + ``match_task`` for heavy work.
    """
    try:
        from st_aggrid import AgGrid
        from st_aggrid.shared import GridUpdateMode
    except ImportError as exc:
        raise ImportError(
            'DataGrid requires streamlit-aggrid. Install with: pip install "streamtree[tables]"'
        ) from exc

    update_mode = GridUpdateMode.NO_UPDATE
    if el.editable:
        update_mode |= GridUpdateMode.VALUE_CHANGED
    if el.selection_mode != "none":
        update_mode |= GridUpdateMode.SELECTION_CHANGED

    grid_options = _merge_grid_options(el)
    data = _coerce_dataframe(el.data)
    kw: dict[str, Any] = {
        "data": data,
        "gridOptions": grid_options or None,
        "height": el.height,
        "update_mode": update_mode,
        "key": widget_key,
    }
    result = AgGrid(**kw)
    if el.on_result is not None:
        el.on_result(result)


__all__ = ["DataGrid", "render_datagrid"]
