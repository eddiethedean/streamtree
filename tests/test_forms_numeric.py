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


class WithSeven(BaseModel):
    n: int = 7


class OptionalNonNoneDefault(BaseModel):
    n: int | None = 15


class IntDefaultFactory(BaseModel):
    n: int = Field(default_factory=lambda: 9)


class OptionalIntFactory(BaseModel):
    n: int | None = Field(default_factory=lambda: 4)


class OptionalBare(BaseModel):
    n: int | None


class BareInt(BaseModel):
    n: int


class IntCoerceFactory(BaseModel):
    n: int = Field(default_factory=list)


class OptionalCoerceFactory(BaseModel):
    n: int | None = Field(default_factory=list)


class BareFloat(BaseModel):
    x: float


class FloatBadFactory(BaseModel):
    x: float = Field(default_factory=list)


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


def test_optional_numeric_initial_session_is_none() -> None:
    with render_context("onone"):
        b = bind_numeric_fields(OptionalNums, key_prefix="onz")
        assert b["n"]() is None
        assert b["x"]() is None


def test_bind_numeric_respects_model_defaults() -> None:
    with render_context("pdef"):
        b = bind_numeric_fields(PricedItem, key_prefix="pf")
        assert b["count"]() == 0
        assert b["unit_price"]() == 0.0


def test_bind_numeric_nonzero_int_default() -> None:
    with render_context("s7"):
        b = bind_numeric_fields(WithSeven, key_prefix="w7")
        assert b["n"]() == 7


def test_optional_numeric_respects_non_none_default() -> None:
    with render_context("ond"):
        b = bind_numeric_fields(OptionalNonNoneDefault, key_prefix="x")
        assert b["n"]() == 15


def test_bind_numeric_default_factory() -> None:
    with render_context("dff"):
        b = bind_numeric_fields(IntDefaultFactory, key_prefix="df")
        assert b["n"]() == 9


def test_optional_numeric_default_factory() -> None:
    with render_context("oidf"):
        b = bind_numeric_fields(OptionalIntFactory, key_prefix="oif")
        assert b["n"]() == 4


def test_optional_numeric_no_field_default_uses_none() -> None:
    with render_context("obare"):
        b = bind_numeric_fields(OptionalBare, key_prefix="ob")
        assert b["n"]() is None


def test_required_int_no_default_uses_zero() -> None:
    with render_context("bi"):
        b = bind_numeric_fields(BareInt, key_prefix="b")
        assert b["n"]() == 0


def test_required_int_factory_non_numeric_coerces_to_zero() -> None:
    with render_context("icf"):
        b = bind_numeric_fields(IntCoerceFactory, key_prefix="ic")
        assert b["n"]() == 0


def test_optional_int_factory_non_numeric_yields_none() -> None:
    with render_context("ocf"):
        b = bind_numeric_fields(OptionalCoerceFactory, key_prefix="oc")
        assert b["n"]() is None


def test_required_float_no_default_uses_zero() -> None:
    with render_context("bf"):
        b = bind_numeric_fields(BareFloat, key_prefix="bf")
        assert b["x"]() == 0.0


def test_required_float_factory_non_numeric_coerces_to_zero() -> None:
    with render_context("fbf"):
        b = bind_numeric_fields(FloatBadFactory, key_prefix="fb")
        assert b["x"]() == 0.0


def test_internal_optional_union_detection() -> None:
    from typing import Literal, Union

    from streamtree.forms import _is_optional_numeric_union

    assert _is_optional_numeric_union(int | None) is True
    assert _is_optional_numeric_union(Union[int, None]) is True  # noqa: UP007
    assert _is_optional_numeric_union(int) is False
    assert _is_optional_numeric_union(Literal[1]) is False


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
