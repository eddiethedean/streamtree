"""Tests for streamtree.asyncio (background submit + poll)."""

from __future__ import annotations

import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from streamtree.asyncio import TaskHandle, submit


def test_submit_completes() -> None:
    st = SimpleNamespace(session_state={})
    done = threading.Event()

    def work() -> int:
        done.set()
        return 7

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="job1")
        assert isinstance(h, TaskHandle)
        assert done.wait(timeout=2.0)
        assert h.status() == "done"
        assert h.result() == 7
        assert h.error() is None


def test_submit_rejects_blank_key() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st), pytest.raises(ValueError):
        submit(lambda: 1, key="  ")  # type: ignore[arg-type]


def test_submit_error_surface() -> None:
    st = SimpleNamespace(session_state={})
    done = threading.Event()

    def boom() -> None:
        done.set()
        raise RuntimeError("x")

    with patch("streamtree.asyncio.st", st):
        h = submit(boom, key="job_err")
        assert done.wait(timeout=2.0)
        assert h.status() == "error"
        assert h.error() is not None
        assert "RuntimeError" in h.error()  # type: ignore[operator]


def test_cancel_before_thread_starts() -> None:
    st = SimpleNamespace(session_state={})
    with (
        patch("streamtree.asyncio.st", st),
        patch.object(threading.Thread, "start", lambda self: None),
    ):
        h = submit(lambda: 1, key="job_cancel")
        h.cancel()
    assert st.session_state["streamtree.asyncio.task.job_cancel"]["status"] == "cancelled"


def test_task_handle_missing_session() -> None:
    st = SimpleNamespace(session_state={})
    h = TaskHandle(_session_key="streamtree.asyncio.task.nope")
    with patch("streamtree.asyncio.st", st):
        assert h.status() == "missing"
        assert h.result() is None
        assert h.error() is None


def test_cancel_handles_missing_session() -> None:
    st = SimpleNamespace(session_state={})
    h = TaskHandle(_session_key="streamtree.asyncio.task.none")
    with patch("streamtree.asyncio.st", st):
        h.cancel()


def test_submit_idempotent_same_key() -> None:
    st = SimpleNamespace(session_state={})
    n = {"c": 0}

    def work() -> int:
        n["c"] += 1
        return n["c"]

    with patch("streamtree.asyncio.st", st):
        h1 = submit(work, key="idem")
        h2 = submit(work, key="idem")
        assert h1._session_key == h2._session_key
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h1.status() == "done":
                break
            time.sleep(0.01)
        assert h1.result() == 1
        assert n["c"] == 1


def test_submit_passes_args_and_kwargs_to_fn() -> None:
    st = SimpleNamespace(session_state={})
    done = threading.Event()

    def work(a: int, b: int = 0) -> int:
        done.set()
        return a + b

    with patch("streamtree.asyncio.st", st):
        h = submit(work, 3, key="args_kw", b=4)
        assert done.wait(timeout=2.0)
        assert h.result() == 7


def test_cancel_is_noop_when_not_pending() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.job_running"
    st.session_state[sk] = {
        "status": "running",
        "result": None,
        "error": None,
        "_submitted": True,
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        h.cancel()
    assert st.session_state[sk]["status"] == "running"


def test_task_handle_status_coerces_non_str() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.coerce"
    st.session_state[sk] = {
        "status": 42,
        "result": None,
        "error": None,
        "_submitted": True,
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        assert h.status() == "42"


def test_task_handle_error_coerces_non_str() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.err_coerce"
    st.session_state[sk] = {
        "status": "error",
        "result": None,
        "error": 404,
        "_submitted": True,
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        assert h.error() == "404"


def test_submit_run_aborts_when_cancelled_before_fn() -> None:
    """Exercise ``mark_running_or_abort`` when status is already ``cancelled``."""
    st = SimpleNamespace(session_state={})
    ran: list[int] = []

    def work() -> int:
        ran.append(1)
        return 42

    captured: dict[str, object] = {}

    def capture_start(self: threading.Thread) -> None:
        captured["target"] = self._target
        captured["args"] = self._args

    with patch("streamtree.asyncio.st", st), patch.object(threading.Thread, "start", capture_start):
        submit(work, key="pre_cancel")

    sk = "streamtree.asyncio.task.pre_cancel"
    st.session_state[sk]["status"] = "cancelled"
    target = captured["target"]
    assert callable(target)
    target(*captured["args"])
    assert ran == []
    assert st.session_state[sk]["status"] == "cancelled"
