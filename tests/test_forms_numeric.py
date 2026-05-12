"""Tests for numeric Pydantic form helpers."""

from __future__ import annotations

from typing import Annotated

import pytest
from pydantic import BaseModel, Field

from streamtree.core.context import render_context
from streamtree.forms import (
    bind_numeric_fields,
    number_inputs,
    numeric_field_names,
)


class PricedItem(BaseModel):
    count: int = 0
    unit_price: float = 0.0


class OptionalNums(BaseModel):
    n: int | None = None
    x: float | None = None


class AnnotatedInt(BaseModel):
    k: Annotated[int, Field(ge=0)] = 0


def test_numeric_field_names_order() -> None:
    assert numeric_field_names(PricedItem) == ("count", "unit_price")


def test_bind_and_number_inputs() -> None:
    with render_context("nf"):
        b = bind_numeric_fields(PricedItem, key_prefix="p1")
        assert set(b) == {"count", "unit_price"}
        widgets = number_inputs(PricedItem, bindings=b)
        assert len(widgets) == 2
        assert widgets[0].label
        assert widgets[1].label


def test_number_inputs_missing_binding() -> None:
    with render_context("nf2"), pytest.raises(ValueError, match="missing"):
        number_inputs(PricedItem, bindings={})


def test_bind_numeric_rejects_blank_prefix() -> None:
    with render_context("nf3"), pytest.raises(ValueError):
        bind_numeric_fields(PricedItem, key_prefix="  ")


def test_no_numeric_fields_empty() -> None:
    class OnlyStr(BaseModel):
        name: str

    with render_context("nf4"):
        assert bind_numeric_fields(OnlyStr, key_prefix="z") == {}
        assert number_inputs(OnlyStr, bindings={}) == ()


def test_optional_numeric_fields_included() -> None:
    assert numeric_field_names(OptionalNums) == ("n", "x")
    with render_context("optn"):
        b = bind_numeric_fields(OptionalNums, key_prefix="on")
        assert set(b) == {"n", "x"}
        assert len(number_inputs(OptionalNums, bindings=b)) == 2


def test_numeric_field_names_rejects_multi_union() -> None:
    class IntStrNone(BaseModel):
        x: int | str | None = None

    assert numeric_field_names(IntStrNone) == ()


def test_numeric_field_names_rejects_optional_non_scalar() -> None:
    class ListIntNone(BaseModel):
        xs: list[int] | None = None

    assert numeric_field_names(ListIntNone) == ()


def test_annotated_int_field() -> None:
    with render_context("nf5"):
        b = bind_numeric_fields(AnnotatedInt, key_prefix="ai")
        assert set(b) == {"k"}
        (w,) = number_inputs(AnnotatedInt, bindings=b)
        assert w.label
