"""Tests for ``streamtree.loading``."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import pytest

from streamtree.core.element import Element
from streamtree.elements import Text, VStack
from streamtree.loading import match_task, match_task_many


@dataclass
class _FakeHandle:
    _status: str
    _result: Any = None
    _error: str | None = None

    def status(self) -> str:
        return self._status

    def result(self) -> Any:
        return self._result

    def error(self) -> str | None:
        return self._error


def _t(s: str) -> Element:
    return Text(s)


def test_match_task_pending_running_missing() -> None:
    for st in ("pending", "running", "missing"):
        out = match_task(
            _FakeHandle(st),
            loading=VStack(_t("L")),
            ready=lambda x: VStack(_t(f"R{x}")),
            error=VStack(_t("E")),
        )
        assert isinstance(out, VStack)


def test_match_task_done_calls_ready() -> None:
    out = match_task(
        _FakeHandle("done", _result=7),
        loading=VStack(_t("L")),
        ready=lambda x: VStack(_t(f"got:{x}")),
        error=VStack(_t("E")),
    )
    tree = out.children[0]
    assert isinstance(tree, Text)
    assert tree.body == "got:7"


def test_match_task_error_branch() -> None:
    out = match_task(
        _FakeHandle("error", _error="boom"),
        loading=VStack(_t("L")),
        ready=lambda x: VStack(_t("R")),
        error=VStack(_t("E")),
    )
    assert isinstance(out, VStack)


def test_match_task_cancelled_prefers_custom() -> None:
    out = match_task(
        _FakeHandle("cancelled"),
        loading=VStack(_t("L")),
        ready=lambda x: VStack(_t("R")),
        error=VStack(_t("E")),
        cancelled=VStack(_t("X")),
    )
    assert isinstance(out, VStack)
    assert isinstance(out.children[0], Text)
    assert out.children[0].body == "X"


def test_match_task_cancelled_falls_back_to_error() -> None:
    out = match_task(
        _FakeHandle("cancelled"),
        loading=VStack(_t("L")),
        ready=lambda x: VStack(_t("R")),
        error=VStack(_t("E")),
    )
    assert isinstance(out.children[0], Text)
    assert out.children[0].body == "E"


def test_match_task_unknown_status_uses_loading(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="streamtree.loading"):
        out = match_task(
            _FakeHandle("weird"),
            loading=VStack(_t("L")),
            ready=lambda x: VStack(_t("R")),
            error=VStack(_t("E")),
        )
    assert isinstance(out.children[0], Text)
    assert out.children[0].body == "L"
    assert "unknown task status" in caplog.text and "weird" in caplog.text


def test_match_task_done_ready_raises_propagates() -> None:
    def boom(_: Any) -> Element:
        raise ValueError("nope")

    with pytest.raises(ValueError, match="nope"):
        match_task(
            _FakeHandle("done", _result=1),
            loading=VStack(_t("L")),
            ready=boom,
            error=VStack(_t("E")),
        )


def test_match_task_many_empty_all_done() -> None:
    out = match_task_many(
        [],
        loading=VStack(_t("L")),
        ready=lambda xs: VStack(_t(f"n={len(xs)}")),
        error=VStack(_t("E")),
    )
    assert isinstance(out.children[0], Text)
    assert out.children[0].body == "n=0"


def test_match_task_many_all_done_tuple() -> None:
    out = match_task_many(
        [_FakeHandle("done", _result=1), _FakeHandle("done", _result=2)],
        loading=VStack(_t("L")),
        ready=lambda xs: VStack(_t(f"{xs}")),
        error=VStack(_t("E")),
    )
    assert out.children[0].body == "(1, 2)"


def test_match_task_many_one_pending_uses_loading() -> None:
    out = match_task_many(
        [_FakeHandle("done", _result=1), _FakeHandle("pending")],
        loading=VStack(_t("L")),
        ready=lambda xs: VStack(_t("R")),
        error=VStack(_t("E")),
    )
    assert out.children[0].body == "L"


def test_match_task_many_any_error() -> None:
    out = match_task_many(
        [_FakeHandle("done", _result=1), _FakeHandle("error", _error="x")],
        loading=VStack(_t("L")),
        ready=lambda xs: VStack(_t("R")),
        error=VStack(_t("E")),
    )
    assert out.children[0].body == "E"


def test_match_task_many_cancelled_custom() -> None:
    out = match_task_many(
        [_FakeHandle("cancelled"), _FakeHandle("done", _result=0)],
        loading=VStack(_t("L")),
        ready=lambda xs: VStack(_t("R")),
        error=VStack(_t("E")),
        cancelled=VStack(_t("X")),
    )
    assert out.children[0].body == "X"


def test_match_task_many_unknown_status(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG, logger="streamtree.loading"):
        out = match_task_many(
            [_FakeHandle("done", _result=1), _FakeHandle("weird")],
            loading=VStack(_t("L")),
            ready=lambda xs: VStack(_t("R")),
            error=VStack(_t("E")),
        )
    assert out.children[0].body == "L"
    assert "match_task_many" in caplog.text and "weird" in caplog.text
