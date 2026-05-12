"""Package metadata exposed at import time."""

from __future__ import annotations

import streamtree


def test_version_matches_release_series() -> None:
    assert streamtree.__version__ == "0.2.0"
