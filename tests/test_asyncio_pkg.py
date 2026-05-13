"""Tests for streamtree.asyncio (background submit + poll)."""

from __future__ import annotations

import threading
import time
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from streamtree.asyncio import (
    TaskHandle,
    complete_cancelled,
    dismiss_task,
    is_task_cancel_requested,
    set_task_progress,
    submit,
    submit_many,
)


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
        assert h.progress() is None


def test_submit_worker_sets_progress() -> None:
    st = SimpleNamespace(session_state={})
    done = threading.Event()

    def work() -> int:
        set_task_progress(key="prog_job", value="step-a")
        set_task_progress(key="prog_job", value="step-b")
        done.set()
        return 42

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="prog_job")
        assert done.wait(timeout=2.0)
        assert h.status() == "done"
        assert h.progress() == "step-b"
        assert h.result() == 42


def test_set_task_progress_noop_when_task_missing() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        set_task_progress(key="nope", value=1)


def test_task_handle_progress_missing_session() -> None:
    st = SimpleNamespace(session_state={})
    h = TaskHandle(_session_key="streamtree.asyncio.task.none")
    with patch("streamtree.asyncio.st", st):
        assert h.progress() is None


def test_set_task_progress_rejects_blank_key() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st), pytest.raises(ValueError):
        set_task_progress(key="  ", value=1)  # type: ignore[arg-type]


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


def test_submit_replaces_corrupted_session_dict() -> None:
    """A non-task dict at the session key is removed and a real submit proceeds."""
    st = SimpleNamespace(session_state={})
    st.session_state["streamtree.asyncio.task.bad"] = {"not": "a task box"}
    ran: list[int] = []

    def work() -> int:
        ran.append(1)
        return 99

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="bad")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "done":
                break
            time.sleep(0.01)
        assert h.result() == 99
        assert ran == [1]
        box = st.session_state["streamtree.asyncio.task.bad"]
        assert box.get("_submitted") is True


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


def test_cancel_running_requests_cooperative_cancel() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.job_running"
    st.session_state[sk] = {
        "status": "running",
        "result": None,
        "error": None,
        "progress": None,
        "cancel_requested": False,
        "_submitted": True,
        "_lock": threading.Lock(),
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        h.cancel()
    box = st.session_state[sk]
    assert box["status"] == "running"
    assert box["cancel_requested"] is True


def test_task_handle_status_coerces_non_str() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.coerce"
    st.session_state[sk] = {
        "status": 42,
        "result": None,
        "error": None,
        "progress": None,
        "_submitted": True,
        "_lock": threading.Lock(),
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
        "progress": None,
        "_submitted": True,
        "_lock": threading.Lock(),
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


def test_submit_worker_progress_poll_while_running() -> None:
    """Progress updates are visible while status is still ``running``."""
    st = SimpleNamespace(session_state={})
    proceed = threading.Event()

    def work() -> int:
        set_task_progress(key="poll_run", value=0)
        assert proceed.wait(timeout=2.0)
        set_task_progress(key="poll_run", value=100)
        return 1

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="poll_run")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "running" and h.progress() == 0:
                break
            time.sleep(0.01)
        else:
            pytest.fail("expected running status and progress 0 from worker")
        assert h.status() == "running"
        proceed.set()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "done":
                break
            time.sleep(0.01)
        assert h.status() == "done"
        assert h.progress() == 100
        assert h.result() == 1


def test_submit_error_preserves_last_progress() -> None:
    st = SimpleNamespace(session_state={})
    done = threading.Event()

    def work() -> None:
        set_task_progress(key="err_prog", value={"step": 2})
        done.set()
        raise ValueError("boom")

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="err_prog")
        assert done.wait(timeout=2.0)
        assert h.status() == "error"
        assert h.progress() == {"step": 2}
        assert h.result() is None


def test_task_handle_progress_missing_progress_key() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.no_prog_key"
    st.session_state[sk] = {
        "status": "running",
        "result": None,
        "error": None,
        "_submitted": True,
        "_lock": threading.Lock(),
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        assert h.progress() is None


def test_task_handle_progress_ignores_box_without_real_lock() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.bad_lock"
    st.session_state[sk] = {
        "status": "done",
        "result": 1,
        "error": None,
        "progress": {"pct": 50},
        "_submitted": True,
        "_lock": "not-a-lock",
    }
    h = TaskHandle(_session_key=sk)
    with patch("streamtree.asyncio.st", st):
        assert h.progress() is None


def test_set_task_progress_from_main_thread_updates_worker_box() -> None:
    """Callers may set progress from the main rerun thread as well as the worker."""
    st = SimpleNamespace(session_state={})
    started = threading.Event()

    def work() -> int:
        started.set()
        time.sleep(0.35)
        return 99

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="main_set_prog")
        assert started.wait(timeout=2.0)
        set_task_progress(key="main_set_prog", value="main-thread")
        assert h.progress() == "main-thread"
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "done":
                break
            time.sleep(0.01)
        assert h.result() == 99


def test_with_box_lock_runs_fn_when_lock_missing() -> None:
    import streamtree.asyncio as aio_mod

    assert aio_mod._with_box_lock({"_lock": "not-a-lock"}, lambda: 42) == 42


def test_set_task_progress_noop_for_foreign_dict_at_task_key() -> None:
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.foreign"
    st.session_state[sk] = {"note": "not a task box"}
    with patch("streamtree.asyncio.st", st):
        set_task_progress(key="foreign", value="x")
    assert st.session_state[sk] == {"note": "not a task box"}


def test_submit_replaces_submitted_flag_without_lock() -> None:
    """``_submitted`` alone is not trusted; missing real lock is replaced like a foreign dict."""
    st = SimpleNamespace(session_state={})
    sk = "streamtree.asyncio.task.nolock"
    st.session_state[sk] = {"_submitted": True, "status": "pending"}
    ran: list[int] = []

    def work() -> int:
        ran.append(1)
        return 5

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="nolock")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "done":
                break
            time.sleep(0.01)
        assert h.result() == 5
        assert ran == [1]
        box = st.session_state[sk]
        assert box.get("_submitted") is True
        lk = box["_lock"]
        assert hasattr(lk, "acquire") and hasattr(lk, "release")


def test_is_task_cancel_requested_false_when_missing() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        assert is_task_cancel_requested(key="nope") is False


def test_complete_cancelled_noop_when_missing() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        complete_cancelled(key="nope")


def test_submit_many_completes_two_tasks() -> None:
    st = SimpleNamespace(session_state={})

    def a() -> int:
        return 1

    def b() -> int:
        return 2

    with patch("streamtree.asyncio.st", st):
        h1, h2 = submit_many((("ja", a), ("jb", b)))
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h1.status() == "done" and h2.status() == "done":
                break
            time.sleep(0.01)
        assert h1.result() == 1
        assert h2.result() == 2


def test_submit_many_empty() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        assert submit_many(()) == ()


def test_submit_many_duplicate_keys() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st), pytest.raises(ValueError, match="duplicate"):
        submit_many((("x", lambda: 1), ("x", lambda: 2)))


def test_submit_many_blank_key() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st), pytest.raises(ValueError, match="non-empty"):
        submit_many((("  ", lambda: 1),))


def test_cooperative_cancel_while_running() -> None:
    st = SimpleNamespace(session_state={})
    started = threading.Event()
    proceed = threading.Event()

    def work() -> int | None:
        started.set()
        assert proceed.wait(timeout=2.0)
        if is_task_cancel_requested(key="coop"):
            complete_cancelled(key="coop")
            return None
        return 99

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="coop")
        assert started.wait(timeout=2.0)
        assert h.status() == "running"
        h.cancel()
        proceed.set()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "cancelled":
                break
            time.sleep(0.01)
        assert h.status() == "cancelled"
        assert h.result() is None


def test_normal_completion_wins_over_cancel_requested() -> None:
    st = SimpleNamespace(session_state={})
    started = threading.Event()
    proceed = threading.Event()

    def work() -> int:
        started.set()
        assert proceed.wait(timeout=2.0)
        return 42

    with patch("streamtree.asyncio.st", st):
        h = submit(work, key="win")
        assert started.wait(timeout=2.0)
        h.cancel()
        assert is_task_cancel_requested(key="win")
        proceed.set()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            if h.status() == "done":
                break
            time.sleep(0.01)
        assert h.status() == "done"
        assert h.result() == 42


def test_dismiss_task_clears_done_and_allows_resubmit() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        h = submit(lambda: 7, key="reuse")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and h.status() != "done":
            time.sleep(0.01)
        assert dismiss_task(key="reuse") is True
        assert "streamtree.asyncio.task.reuse" not in st.session_state
        h2 = submit(lambda: 8, key="reuse")
        deadline2 = time.monotonic() + 2.0
        while time.monotonic() < deadline2 and h2.status() != "done":
            time.sleep(0.01)
        assert h2.result() == 8


def test_dismiss_task_false_while_running() -> None:
    st = SimpleNamespace(session_state={})
    started = threading.Event()
    hold = threading.Event()

    def slow() -> int:
        started.set()
        assert hold.wait(timeout=2.0)
        return 1

    with patch("streamtree.asyncio.st", st):
        h = submit(slow, key="slowjob")
        assert started.wait(timeout=2.0)
        assert h.status() == "running"
        assert dismiss_task(key="slowjob") is False
        assert "streamtree.asyncio.task.slowjob" in st.session_state
        hold.set()
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and h.status() != "done":
            time.sleep(0.01)


def test_dismiss_task_missing_key() -> None:
    st = SimpleNamespace(session_state={})
    with patch("streamtree.asyncio.st", st):
        assert dismiss_task(key="nope") is False


def test_dismiss_task_removes_foreign_mapping() -> None:
    st = SimpleNamespace(session_state={"streamtree.asyncio.task.foreign": {"not": "managed"}})
    with patch("streamtree.asyncio.st", st):
        assert dismiss_task(key="foreign") is True
        assert "streamtree.asyncio.task.foreign" not in st.session_state
