"""Tests for ``streamtree.auth`` helpers."""

from __future__ import annotations

import pytest
import streamlit_authenticator


def test_build_authenticator_passes_cookie_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeAuth:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(streamlit_authenticator, "Authenticate", FakeAuth)
    from streamtree.auth import build_authenticator

    build_authenticator(
        {
            "credentials": {"usernames": {}},
            "cookie": {"name": "cn", "key": "ck", "expiry_days": 7},
        }
    )
    assert captured["cookie_name"] == "cn"
    assert captured["cookie_key"] == "ck"
    assert captured["cookie_expiry_days"] == 7.0


def test_build_authenticator_default_expiry(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class FakeAuth:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

    monkeypatch.setattr(streamlit_authenticator, "Authenticate", FakeAuth)
    from streamtree.auth import build_authenticator

    build_authenticator({"credentials": {}, "cookie": {"name": "n", "key": "k"}})
    assert captured["cookie_expiry_days"] == 30.0


def test_build_authenticator_missing_credentials_raises() -> None:
    from streamtree.auth import build_authenticator

    with pytest.raises(ValueError, match="credentials"):
        build_authenticator({"cookie": {"name": "n", "key": "k"}})


def test_build_authenticator_missing_cookie_key_raises() -> None:
    from streamtree.auth import build_authenticator

    with pytest.raises(ValueError, match="key"):
        build_authenticator({"credentials": {}, "cookie": {"name": "n"}})
