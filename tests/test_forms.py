"""Tests for streamtree.forms."""

from __future__ import annotations

import json
from typing import Annotated

import pytest
from pydantic import BaseModel, ValidationError

from streamtree import forms as forms_mod
from streamtree.forms import format_validation_errors, model_validate_json, str_field_names


class Sample(BaseModel):
    name: str
    nick: str | None = None
    age: int = 0


def test_str_field_names() -> None:
    assert str_field_names(Sample) == ("name", "nick")


def test_str_field_names_empty_model() -> None:
    class Empty(BaseModel):
        x: int

    assert str_field_names(Empty) == ()


def test_model_validate_json_ok() -> None:
    m = model_validate_json(Sample, '{"name": "Ada", "age": 1}')
    assert m.name == "Ada"
    assert m.age == 1


def test_model_validate_json_empty_object() -> None:
    with pytest.raises(ValidationError):
        model_validate_json(Sample, "")


def test_model_validate_json_bad_json() -> None:
    with pytest.raises(json.JSONDecodeError):
        model_validate_json(Sample, "not json")


def test_model_validate_json_not_object() -> None:
    with pytest.raises(TypeError):
        model_validate_json(Sample, "[1,2]")


def test_str_field_names_includes_annotated_str() -> None:
    class WithMeta(BaseModel):
        name: Annotated[str, "display"]

    assert str_field_names(WithMeta) == ("name",)


def test_str_field_names_double_annotated() -> None:
    class Nested(BaseModel):
        name: Annotated[Annotated[str, "a"], "b"]

    assert str_field_names(Nested) == ("name",)


def test_unwrap_annotation_peels_metadata() -> None:
    ann = Annotated[str, "meta", 2]
    assert forms_mod._unwrap_annotation(ann) is str


def test_unwrap_annotation_nested() -> None:
    ann = Annotated[Annotated[str, 1], 2]
    assert forms_mod._unwrap_annotation(ann) is str


def test_format_validation_errors() -> None:
    try:
        Sample.model_validate({"name": 1})
    except ValidationError as e:
        text = format_validation_errors(e)
        assert "name" in text


def test_format_validation_errors_multiple_fields() -> None:
    try:
        Sample.model_validate({"name": 1, "age": "x"})
    except ValidationError as e:
        text = format_validation_errors(e)
        assert "name" in text
        assert "age" in text
        assert text.count("\n") >= 1
