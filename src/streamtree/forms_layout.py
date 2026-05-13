"""Layout helpers for Pydantic-bound forms (rows / columns)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TypeVar

from pydantic import BaseModel

from streamtree.elements.layout import Columns, VStack
from streamtree.elements.widgets import Checkbox, NumberInput, TextInput
from streamtree.forms import (
    NumericStateVar,
    bool_field_names,
    numeric_field_names,
    str_field_names,
)
from streamtree.state import StateVar

M = TypeVar("M", bound=BaseModel)


def build_model_from_bindings(
    model_cls: type[M],
    *,
    str_bindings: Mapping[str, StateVar[str]],
    numeric_bindings: Mapping[str, NumericStateVar],
    bool_bindings: Mapping[str, StateVar[bool]] | None = None,
) -> M:
    """Build ``model_cls`` from current ``StateVar`` values (strict validation)."""
    bb = bool_bindings or {}
    data: dict[str, object] = {}
    for n in str_field_names(model_cls):
        if n not in str_bindings:
            raise ValueError(f"missing str binding for field {n!r}")
        data[n] = str_bindings[n]()
    for n in numeric_field_names(model_cls):
        if n not in numeric_bindings:
            raise ValueError(f"missing numeric binding for field {n!r}")
        data[n] = numeric_bindings[n]()
    for n in bool_field_names(model_cls):
        if n not in bb:
            raise ValueError(f"missing bool binding for field {n!r}")
        data[n] = bb[n]()
    return model_cls.model_validate(data)


def model_field_grid(
    model_cls: type[BaseModel],
    rows: tuple[tuple[str, ...], ...],
    *,
    str_bindings: Mapping[str, StateVar[str]],
    numeric_bindings: Mapping[str, NumericStateVar],
    bool_bindings: Mapping[str, StateVar[bool]] | None = None,
    field_labels: Mapping[str, str] | None = None,
) -> VStack:
    """Stack ``Columns`` rows: each inner tuple names fields rendered left-to-right in one row."""
    if not rows:
        raise ValueError("rows must contain at least one row")
    bb = bool_bindings or {}
    str_names = set(str_field_names(model_cls))
    num_names = set(numeric_field_names(model_cls))
    bool_names = set(bool_field_names(model_cls))
    labels = field_labels or {}
    out_rows: list[Columns] = []
    for row in rows:
        cells: list[Checkbox | NumberInput | TextInput] = []
        for name in row:
            if name in str_names:
                if name not in str_bindings:
                    raise ValueError(f"missing str binding for field {name!r}")
                lab = labels.get(name, name.replace("_", " ").title())
                cells.append(TextInput(lab, value=str_bindings[name]))
            elif name in num_names:
                if name not in numeric_bindings:
                    raise ValueError(f"missing numeric binding for field {name!r}")
                lab = labels.get(name, name.replace("_", " ").title())
                cells.append(NumberInput(lab, value=numeric_bindings[name]))
            elif name in bool_names:
                if name not in bb:
                    raise ValueError(f"missing bool binding for field {name!r}")
                lab = labels.get(name, name.replace("_", " ").title())
                cells.append(Checkbox(lab, value=bb[name]))
            else:
                raise ValueError(
                    f"field {name!r} is not a str, numeric, or bool field on {model_cls.__name__}"
                )
        out_rows.append(Columns(*cells, weights=tuple(1.0 for _ in cells)))
    return VStack(*out_rows)


__all__ = ["build_model_from_bindings", "model_field_grid"]
