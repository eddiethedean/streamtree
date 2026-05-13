"""Tests for ``streamtree.asyncio.summarize_async_tasks``."""

from __future__ import annotations

import threading
from types import SimpleNamespace

import pytest

import streamtree.asyncio as aio


def test_summarize_async_tasks_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_st = SimpleNamespace(session_state={"unrelated.key": 1})
    monkeypatch.setattr(aio, "st", fake_st)
    assert aio.summarize_async_tasks() == []


def test_summarize_async_tasks_managed_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    box = {
        "_submitted": True,
        "_lock": threading.Lock(),
        "status": "running",
        "result": None,
        "error": None,
        "progress": {"pct": 50},
        "cancel_requested": True,
    }
    store = {
        "streamtree.asyncio.task.alpha": box,
        "streamtree.asyncio.task.beta": {"not": "managed"},
        "streamtree.memo.other": 1,
    }
    fake_st = SimpleNamespace(session_state=store)
    monkeypatch.setattr(aio, "st", fake_st)
    rows = aio.summarize_async_tasks()
    assert len(rows) == 1
    assert rows[0]["key"] == "alpha"
    assert rows[0]["status"] == "running"
    assert rows[0]["cancel_requested"] is True
    assert "pct" in rows[0]["progress"]


def test_summarize_async_tasks_long_progress_truncated(monkeypatch: pytest.MonkeyPatch) -> None:
    long_prog = "x" * 200
    box = {
        "_submitted": True,
        "_lock": threading.Lock(),
        "status": "done",
        "result": 1,
        "error": None,
        "progress": long_prog,
        "cancel_requested": False,
    }
    fake_st = SimpleNamespace(session_state={"streamtree.asyncio.task.p": box})
    monkeypatch.setattr(aio, "st", fake_st)
    rows = aio.summarize_async_tasks()
    assert len(rows) == 1
    assert rows[0]["progress"].endswith("...")
    assert len(rows[0]["progress"]) <= 123
