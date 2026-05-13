"""Tests for Phase 3 thin modules: ``crud``, ``enterprise``, ``perf``."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from streamtree.app_context import provider
from streamtree.core.context import render_context
from streamtree.crud import save_intent_counter, selected_id_from_query
from streamtree.enterprise import EVENT_SINK_KEY, emit_event, redact_secrets, tenant_id
from streamtree.perf import PERF_COUNTERS_KEY, perf_bump, perf_snapshot


@pytest.fixture
def mock_st() -> MagicMock:
    m = MagicMock()
    m.session_state = {}
    return m


def test_selected_id_from_query_delegates(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("streamtree.crud.sync_query_value", lambda default, param="id": "rid-9")
    assert selected_id_from_query(param="id") == "rid-9"


def test_save_intent_counter_bump(mock_st: MagicMock) -> None:
    with patch("streamtree.state.st", mock_st):
        with render_context("app"):
            ctr, bump = save_intent_counter(key="sv")
            assert ctr() == 0
            bump()
            assert ctr() == 1


def test_emit_event_no_sink() -> None:
    emit_event("x", {"a": 1})


class RecordingSink:
    """Concrete sink: ``MagicMock`` is not always ``isinstance(..., EventSink)`` on 3.12+."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def emit(self, name: str, payload: Mapping[str, Any]) -> None:
        self.calls.append((name, dict(payload)))


def test_emit_event_calls_sink() -> None:
    sink = RecordingSink()
    with provider(**{EVENT_SINK_KEY: sink}):
        emit_event("evt", {"ok": True})
    assert sink.calls == [("evt", {"ok": True})]


def test_emit_event_skips_lookup_value_that_is_not_event_sink() -> None:
    """Non-protocol values in the bag are ignored (no exception)."""
    with provider(**{EVENT_SINK_KEY: {"not": "a sink"}}):
        emit_event("evt", {"ok": True})


def test_emit_event_empty_name() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        emit_event("  ")


def test_redact_secrets() -> None:
    assert redact_secrets("tok=secret", ("secret",)) == "tok=[REDACTED]"


def test_tenant_id_from_context() -> None:
    with provider(tenant_id="acme"):
        assert tenant_id() == "acme"


def test_tenant_id_none_without_provider() -> None:
    assert tenant_id() is None


def test_perf_bump_and_snapshot() -> None:
    bag: dict[str, int] = {}
    with provider(**{PERF_COUNTERS_KEY: bag}):
        perf_bump("renders")
        perf_bump("renders", delta=2)
        assert perf_snapshot() == {"renders": 3}


def test_perf_bump_noop_without_mutable_bag() -> None:
    perf_bump("x")


def test_perf_snapshot_empty_when_missing() -> None:
    assert perf_snapshot() == {}


def test_perf_snapshot_skips_non_int_values() -> None:
    with provider(**{PERF_COUNTERS_KEY: {"ok": 1, "bad": "nope"}}):
        assert perf_snapshot() == {"ok": 1}


def test_perf_snapshot_non_mapping() -> None:
    with provider(**{PERF_COUNTERS_KEY: "not-a-map"}):
        assert perf_snapshot() == {}
