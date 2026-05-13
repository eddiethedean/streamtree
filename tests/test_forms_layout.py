"""Tests for streamtree.forms_layout."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, Field, ValidationError

from streamtree.forms import bind_numeric_fields, bind_str_fields
from streamtree.forms_layout import build_model_from_bindings, model_field_grid


class RowModel(BaseModel):
    name: str = Field(min_length=1)
    age: int


def test_build_model_from_bindings() -> None:
    sb = bind_str_fields(RowModel, key_prefix="t1")
    nb = bind_numeric_fields(RowModel, key_prefix="t1")
    sb["name"].set("Ada")
    nb["age"].set(40)
    m = build_model_from_bindings(RowModel, str_bindings=sb, numeric_bindings=nb)
    assert m.name == "Ada"
    assert m.age == 40


def test_build_model_from_bindings_validation_error() -> None:
    sb = bind_str_fields(RowModel, key_prefix="t2")
    nb = bind_numeric_fields(RowModel, key_prefix="t2")
    sb["name"].set("")
    nb["age"].set(1)
    with pytest.raises(ValidationError):
        build_model_from_bindings(RowModel, str_bindings=sb, numeric_bindings=nb)


def test_model_field_grid_builds_columns_rows() -> None:
    sb = bind_str_fields(RowModel, key_prefix="g1")
    nb = bind_numeric_fields(RowModel, key_prefix="g1")
    grid = model_field_grid(RowModel, (("name",), ("age",)), str_bindings=sb, numeric_bindings=nb)
    from streamtree.testing import render_to_tree

    tree = render_to_tree(grid)
    assert tree["kind"] == "VStack"
    assert len(tree["children"]) == 2
    assert tree["children"][0]["kind"] == "Columns"


def test_model_field_grid_rejects_unknown_field() -> None:
    sb = bind_str_fields(RowModel, key_prefix="g2")
    nb = bind_numeric_fields(RowModel, key_prefix="g2")
    with pytest.raises(ValueError, match="not a str or numeric"):
        model_field_grid(RowModel, (("nope",),), str_bindings=sb, numeric_bindings=nb)


def test_model_field_grid_requires_row() -> None:
    sb = bind_str_fields(RowModel, key_prefix="g3")
    nb = bind_numeric_fields(RowModel, key_prefix="g3")
    with pytest.raises(ValueError, match="rows"):
        model_field_grid(RowModel, (), str_bindings=sb, numeric_bindings=nb)


def test_build_model_missing_str_binding() -> None:
    nb = bind_numeric_fields(RowModel, key_prefix="ms")
    nb["age"].set(1)
    with pytest.raises(ValueError, match="missing str binding"):
        build_model_from_bindings(RowModel, str_bindings={}, numeric_bindings=nb)


def test_build_model_missing_numeric_binding() -> None:
    sb = bind_str_fields(RowModel, key_prefix="mn")
    sb["name"].set("Ada")
    with pytest.raises(ValueError, match="missing numeric binding"):
        build_model_from_bindings(RowModel, str_bindings=sb, numeric_bindings={})


def test_model_field_grid_missing_str_binding_in_row() -> None:
    nb = bind_numeric_fields(RowModel, key_prefix="gr")
    nb["age"].set(1)
    with pytest.raises(ValueError, match="missing str binding"):
        model_field_grid(RowModel, (("name",),), str_bindings={}, numeric_bindings=nb)


def test_model_field_grid_missing_numeric_binding_in_row() -> None:
    sb = bind_str_fields(RowModel, key_prefix="gn")
    sb["name"].set("Ada")
    with pytest.raises(ValueError, match="missing numeric binding"):
        model_field_grid(RowModel, (("age",),), str_bindings=sb, numeric_bindings={})
