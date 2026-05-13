"""Tests for streamtree.state (mocked Streamlit session)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from streamtree.core.context import render_context
from streamtree.state import (
    StateVar,
    cache,
    form_state,
    memo,
    session_state,
    state,
    toggle_state,
)


@pytest.fixture
def mock_st() -> MagicMock:
    store: dict[str, object] = {}

    m = MagicMock()
    m.session_state = store
    return m


def test_state_explicit_key(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            sv = state(10, key="counter")
            assert isinstance(sv, StateVar)
            assert sv() == 10
            del mock_st.session_state[sv.key]
            assert sv() == 10
            sv.set(11)
            assert sv() == 11
            sv.update(lambda x: x + 1)
            assert sv() == 12
            sv.increment(2)
            assert sv() == 14
            assert sv.key == "streamtree.state.counter"


def test_state_anonymous_key_uses_context(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            a = state("first")
            b = state("second")
            assert a() == "first"
            assert b() == "second"
            assert a.key != b.key


def test_state_increment_non_numeric_raises(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            sv = state("x", key="strstate")
            with pytest.raises(TypeError, match="increment"):
                sv.increment()


def test_toggle_state(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            t = toggle_state(key="tog", initial=False)
            assert t() is False
            t.toggle()
            assert t() is True
            t.set(False)
            assert t() is False
            assert t.key == "streamtree.state.tog"


def test_session_state_reader(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        read = session_state("ext", default=1)
        assert read() == 1
        assert read() == 1


def test_session_state_reader_missing_no_default(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        read = session_state("missing_key")
        with pytest.raises(ValueError, match="unset"):
            read()


def test_session_state_reader_existing_key(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        mock_st.session_state["ext2"] = 42
        read = session_state("ext2")
        assert read() == 42


def test_toggle_state_toggle_twice(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            t = toggle_state(key="tt", initial=True)
            t.toggle()
            t.toggle()
            assert t() is True


def test_form_state_call_reads_committed(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            fs = form_state("only", key="callfs")
            assert fs() == "only"


def test_increment_float_delta(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            sv = state(1.5, key="flt")
            sv.increment(0.5)
            assert sv() == 2.0


def test_form_state_commit(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            fs = form_state("committed", key="fdemo")
            assert "committed" in fs.committed_key or fs.committed_key.endswith("committed")
            assert ".edit" in fs.edit_key
            fs.set_edit("draft")
            assert fs.edit_value() == "draft"
            assert fs() == "committed"
            fs.commit()
            assert fs() == "draft"


def test_memo_and_cache(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        calls = {"n": 0}

        def factory() -> int:
            calls["n"] += 1
            return 7

        assert memo("m1", factory) == 7
        assert memo("m1", factory) == 7
        assert calls["n"] == 1

        assert cache("c1", 99) == 99
        assert cache("c1", 100) == 99
