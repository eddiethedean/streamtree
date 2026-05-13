"""Tests for Portal, PortalMount, and SplitView layout validation."""

from __future__ import annotations

import pytest

from streamtree.elements import Portal, PortalMount, SplitView, Text


def test_portal_requires_non_empty_slot() -> None:
    with pytest.raises(ValueError, match="slot"):
        Portal(slot="  ", child=Text("x"))


def test_portal_mount_requires_non_empty_slot() -> None:
    with pytest.raises(ValueError, match="slot"):
        PortalMount(slot="")


def test_splitview_ratio_bounds() -> None:
    with pytest.raises(ValueError, match="narrow_ratio"):
        SplitView(narrow=Text("a"), main=Text("b"), narrow_ratio=0.0)
    with pytest.raises(ValueError, match="narrow_ratio"):
        SplitView(narrow=Text("a"), main=Text("b"), narrow_ratio=1.0)


def test_splitview_accepts_valid_ratio() -> None:
    s = SplitView(narrow=Text("n"), main=Text("m"), narrow_ratio=0.35)
    assert s.narrow_ratio == 0.35
