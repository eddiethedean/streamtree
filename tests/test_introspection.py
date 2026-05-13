"""Tests for ``streamtree.testing.introspection``."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from streamtree.testing import introspection as intro


def test_iter_and_summarize_session_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    store = {
        "streamtree.state.explicit": 1,
        "streamtree.memo_subtree.app.k.f": {},
        "streamtree.memo.global": {},
        "streamtree.cache.c": {},
        "streamtree.routing.active.route": "x",
        "streamtree.query.value.q": "v",
        "streamtree.widget.w": {},
        "streamtree.app.page_config_applied": True,
        "streamtree.asyncio.task.job": "skip",
        "streamtree.other.slot": 0,
        "unrelated": 9,
    }

    fake_st = SimpleNamespace(session_state=store)
    monkeypatch.setattr(intro, "st", fake_st)

    keys = intro.iter_streamtree_session_keys()
    assert "streamtree.state.explicit" in keys
    assert "unrelated" not in keys

    rows = intro.summarize_streamtree_session_state()
    cats = {r["key"]: r["category"] for r in rows}
    assert cats["streamtree.state.explicit"] == "state_explicit"
    assert cats["streamtree.memo_subtree.app.k.f"] == "memo_subtree"
    assert cats["streamtree.memo.global"] == "memo"
    assert cats["streamtree.cache.c"] == "cache"
    assert cats["streamtree.routing.active.route"] == "routing"
    assert cats["streamtree.query.value.q"] == "query"
    assert cats["streamtree.widget.w"] == "widget"
    assert cats["streamtree.app.page_config_applied"] == "app"
    assert cats["streamtree.asyncio.task.job"] == "async_task"
    assert cats["streamtree.other.slot"] == "other"
