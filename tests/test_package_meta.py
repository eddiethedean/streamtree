"""Package metadata exposed at import time."""

from __future__ import annotations

import streamtree


def test_version_matches_release_series() -> None:
    assert streamtree.__version__ == "0.6.0"


def test_public_exports_are_importable() -> None:
    """Guardrail: top-level ``__all__`` stays aligned with real attributes."""
    for name in streamtree.__all__:
        assert hasattr(streamtree, name), f"missing export: {name!r}"


def test_auth_submodule_exposed() -> None:
    assert hasattr(streamtree, "auth")
    assert hasattr(streamtree.auth, "AuthGate")
    assert hasattr(streamtree.auth, "build_authenticator")


def test_asyncio_and_forms_submodules_exposed() -> None:
    assert hasattr(streamtree.asyncio, "submit")
    assert hasattr(streamtree.asyncio, "set_task_progress")
    assert hasattr(streamtree.asyncio, "TaskHandle")
    assert hasattr(streamtree.forms, "bind_numeric_fields")
    assert hasattr(streamtree.forms, "number_inputs")
    assert hasattr(streamtree.forms, "NumericStateVar")
