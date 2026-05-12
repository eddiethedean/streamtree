"""Pydantic-first helpers for small forms (str fields MVP)."""

from __future__ import annotations

import json
from typing import Annotated, Any, TypeVar, get_args, get_origin

from pydantic import BaseModel, ValidationError

M = TypeVar("M", bound=BaseModel)


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


def str_field_names(model_cls: type[BaseModel]) -> tuple[str, ...]:
    """Field names on ``model_cls`` whose annotation is ``str`` or ``str | None``."""
    return tuple(
        n
        for n, finfo in model_cls.model_fields.items()
        if _is_str_field_annotation(finfo.annotation)
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


__all__ = ["format_validation_errors", "model_validate_json", "str_field_names"]
