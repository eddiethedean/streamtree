"""Tests for declarative str-field form helpers."""

from __future__ import annotations

import pytest
from pydantic import BaseModel

from streamtree.core.context import render_context
from streamtree.forms import bind_str_fields, str_field_names, str_text_inputs


class Person(BaseModel):
    name: str
    nick: str | None = None


class IntOnly(BaseModel):
    n: int = 0


def test_bind_and_str_text_inputs() -> None:
    with render_context("tform"):
        b = bind_str_fields(Person, key_prefix="p1")
        assert set(b) == {"name", "nick"}
        inputs = str_text_inputs(Person, bindings=b)
        assert len(inputs) == len(str_field_names(Person))


def test_str_text_inputs_missing_binding() -> None:
    with render_context("tform2"), pytest.raises(ValueError, match="missing"):
        str_text_inputs(Person, bindings={})


def test_bind_rejects_blank_prefix() -> None:
    with render_context("tform3"), pytest.raises(ValueError):
        bind_str_fields(Person, key_prefix="  ")


def test_no_str_fields_empty_bindings_and_inputs() -> None:
    with render_context("no_str"):
        assert bind_str_fields(IntOnly, key_prefix="z") == {}
        assert str_text_inputs(IntOnly, bindings={}) == ()


def test_str_text_inputs_respects_field_labels() -> None:
    with render_context("labels"):
        b = bind_str_fields(Person, key_prefix="pfx")
        inputs = str_text_inputs(
            Person,
            bindings=b,
            field_labels={"name": "Full name"},
        )
        assert inputs[0].label == "Full name"
        assert inputs[1].label == "Nick"


def test_str_text_inputs_uses_key_prefix_when_no_bindings() -> None:
    with render_context("kp_only"):
        inputs = str_text_inputs(Person, key_prefix="qq")
        assert len(inputs) == 2
        assert all(inp.label for inp in inputs)
