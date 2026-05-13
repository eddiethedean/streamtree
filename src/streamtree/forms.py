"""Pydantic-first helpers for small forms (string and numeric fields)."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from types import UnionType
from typing import Annotated, Any, TypeVar, Union, cast, get_args, get_origin

from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from streamtree.elements.widgets import NumberInput, TextInput
from streamtree.state import StateVar, state

M = TypeVar("M", bound=BaseModel)

NumericStateVar = StateVar[int] | StateVar[float] | StateVar[int | None] | StateVar[float | None]


def _unwrap_annotation(ann: Any) -> Any:
    """Strip :class:`typing.Annotated` wrappers for field-type inspection."""
    while True:
        origin = get_origin(ann)
        if origin is Annotated:
            args = get_args(ann)
            if not args:  # pragma: no cover (Annotated requires >= 2 args at runtime)
                return ann
            ann = args[0]
            continue
        return ann


def _is_str_field_annotation(ann: Any) -> bool:
    ann = _unwrap_annotation(ann)
    if ann is str:
        return True
    origin = get_origin(ann)
    if origin is None:
        return False
    args = [a for a in get_args(ann) if a is not type(None)]
    return len(args) == 1 and args[0] is str


def _numeric_base(ann: Any) -> type[int] | type[float] | None:
    """Return ``int`` or ``float`` for plain or optional numeric fields."""
    ann = _unwrap_annotation(ann)
    if ann is int:
        return int
    if ann is float:
        return float
    origin = get_origin(ann)
    if origin is None:
        return None
    args = [a for a in get_args(ann) if a is not type(None)]
    if len(args) != 1:
        return None
    if args[0] is int:
        return int
    if args[0] is float:
        return float
    return None


def _is_optional_numeric_union(ann: Any) -> bool:
    """True when annotation is a union that includes ``None`` (e.g. ``int | None``)."""
    u = _unwrap_annotation(ann)
    origin = get_origin(u)
    if origin is None:
        return False
    if origin is UnionType or origin is Union:
        return any(a is type(None) for a in get_args(u))
    return False


def _is_bool_field_annotation(ann: Any) -> bool:
    ann = _unwrap_annotation(ann)
    if ann is bool:
        return True
    origin = get_origin(ann)
    if origin is UnionType or origin is Union:
        args = [a for a in get_args(ann) if a is not type(None)]
        return len(args) == 1 and args[0] is bool
    return False


def _initial_bool_for_field(finfo: FieldInfo) -> bool:
    raw: Any
    if finfo.default_factory is not None:
        raw = cast(Callable[[], Any], finfo.default_factory)()
    elif finfo.default is not PydanticUndefined:
        raw = finfo.default
    else:
        return False
    if raw is None:
        return False
    return bool(raw)


def _initial_numeric_for_field(
    finfo: FieldInfo, base: type[int] | type[float], optional: bool
) -> int | float | None:
    """Resolve first session value from field default / factory (Pydantic v2)."""
    raw: Any
    if finfo.default_factory is not None:
        raw = cast(Callable[[], Any], finfo.default_factory)()
    elif finfo.default is not PydanticUndefined:
        raw = finfo.default
    else:
        raw = PydanticUndefined

    if optional:
        if raw is PydanticUndefined or raw is None:
            return None
        if isinstance(raw, (int, float)):
            return raw
        return None
    if raw is PydanticUndefined:
        return 0 if base is int else 0.0
    if isinstance(raw, (int, float)):
        return raw
    return 0 if base is int else 0.0


def str_field_names(model_cls: type[BaseModel]) -> tuple[str, ...]:
    """Field names on ``model_cls`` whose annotation is ``str`` or ``str | None``."""
    return tuple(
        n
        for n, finfo in model_cls.model_fields.items()
        if _is_str_field_annotation(finfo.annotation)
    )


def numeric_field_names(model_cls: type[BaseModel]) -> tuple[str, ...]:
    """Field names whose annotation is ``int`` / ``float`` or optional variants."""
    return tuple(
        n for n, finfo in model_cls.model_fields.items() if _numeric_base(finfo.annotation)
    )


def bool_field_names(model_cls: type[BaseModel]) -> tuple[str, ...]:
    """Field names whose annotation is ``bool`` or ``bool | None``."""
    return tuple(
        n
        for n, finfo in model_cls.model_fields.items()
        if _is_bool_field_annotation(finfo.annotation)
    )


def model_validate_json(model_cls: type[M], raw_json: str) -> M:
    """Parse JSON then :meth:`pydantic.BaseModel.model_validate`.

    Raises :exc:`json.JSONDecodeError` for invalid JSON and
    :class:`pydantic.ValidationError` for schema errors.
    """
    data = json.loads(raw_json) if raw_json.strip() else {}
    if not isinstance(data, dict):
        raise TypeError("JSON document must be an object at the root")
    return model_cls.model_validate(data)


def format_validation_errors(exc: ValidationError) -> str:
    """Human-readable bullet list for UI (e.g. ``Markdown``)."""
    lines: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(x) for x in err.get("loc", ()))
        msg = str(err.get("msg", ""))
        lines.append(f"- **{loc}**: {msg}" if loc else f"- {msg}")
    return "\n".join(lines) if lines else str(exc)


def bind_str_fields(
    model_cls: type[BaseModel],
    *,
    key_prefix: str = "model_form",
) -> dict[str, StateVar[str]]:
    """Create ``StateVar`` strings for each ``str`` / optional-``str`` field."""
    if not key_prefix.strip():
        raise ValueError("key_prefix must be a non-empty string")
    p = key_prefix.strip()
    return {n: state("", key=f"{p}.{n}") for n in str_field_names(model_cls)}


def bind_numeric_fields(
    model_cls: type[BaseModel],
    *,
    key_prefix: str = "model_form",
) -> dict[str, NumericStateVar]:
    """Create numeric ``StateVar`` values for each ``int`` / ``float`` (or optional) field.

    Required ``int`` / ``float`` fields use the model field default when set, otherwise ``0`` /
    ``0.0``. Optional ``int | None`` / ``float | None`` fields use the field default when set,
    otherwise ``None`` (empty number input until the user enters a value).
    """
    if not key_prefix.strip():
        raise ValueError("key_prefix must be a non-empty string")
    p = key_prefix.strip()
    out: dict[str, NumericStateVar] = {}
    for n, finfo in model_cls.model_fields.items():
        base = _numeric_base(finfo.annotation)
        if base is int:
            opt = _is_optional_numeric_union(finfo.annotation)
            init = _initial_numeric_for_field(finfo, int, opt)
            out[n] = state(init, key=f"{p}.{n}")
        elif base is float:
            opt = _is_optional_numeric_union(finfo.annotation)
            init = _initial_numeric_for_field(finfo, float, opt)
            out[n] = state(init, key=f"{p}.{n}")
    return out


def bind_bool_fields(
    model_cls: type[BaseModel],
    *,
    key_prefix: str = "model_form",
) -> dict[str, StateVar[bool]]:
    """Create ``StateVar[bool]`` for each ``bool`` / ``bool | None`` field."""
    if not key_prefix.strip():
        raise ValueError("key_prefix must be a non-empty string")
    p = key_prefix.strip()
    out: dict[str, StateVar[bool]] = {}
    for n in bool_field_names(model_cls):
        finfo = model_cls.model_fields[n]
        out[n] = state(_initial_bool_for_field(finfo), key=f"{p}.{n}")
    return out


def str_text_inputs(
    model_cls: type[BaseModel],
    *,
    bindings: Mapping[str, StateVar[str]] | None = None,
    key_prefix: str = "model_form",
    field_labels: Mapping[str, str] | None = None,
) -> tuple[TextInput, ...]:
    """Build ``TextInput`` widgets for each string field."""
    names = str_field_names(model_cls)
    b: dict[str, StateVar[str]] = (
        dict(bindings)
        if bindings is not None
        else bind_str_fields(model_cls, key_prefix=key_prefix)
    )
    for n in names:
        if n not in b:
            raise ValueError(f"missing StateVar binding for field {n!r}")
    labels = field_labels or {}
    out: list[TextInput] = []
    for n in names:
        label = labels.get(n, n.replace("_", " ").title())
        out.append(TextInput(label, value=b[n]))
    return tuple(out)


def number_inputs(
    model_cls: type[BaseModel],
    *,
    bindings: Mapping[str, NumericStateVar] | None = None,
    key_prefix: str = "model_form",
    field_labels: Mapping[str, str] | None = None,
) -> tuple[NumberInput, ...]:
    """Build ``NumberInput`` widgets for each numeric field."""
    names = numeric_field_names(model_cls)
    b: dict[str, NumericStateVar] = (
        dict(bindings)
        if bindings is not None
        else bind_numeric_fields(model_cls, key_prefix=key_prefix)
    )
    for n in names:
        if n not in b:
            raise ValueError(f"missing StateVar binding for field {n!r}")
    labels = field_labels or {}
    out: list[NumberInput] = []
    for n in names:
        label = labels.get(n, n.replace("_", " ").title())
        out.append(NumberInput(label, value=b[n]))
    return tuple(out)


__all__ = [
    "NumericStateVar",
    "bind_bool_fields",
    "bind_numeric_fields",
    "bind_str_fields",
    "bool_field_names",
    "format_validation_errors",
    "model_validate_json",
    "number_inputs",
    "numeric_field_names",
    "str_field_names",
    "str_text_inputs",
]
