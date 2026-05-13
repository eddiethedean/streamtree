"""Tests for optional ``streamlit-extras`` element validation."""

from __future__ import annotations

import pytest

from streamtree.elements.ui_extra import SocialBadge


def test_social_badge_requires_name_for_pypi() -> None:
    with pytest.raises(ValueError, match="name is required"):
        SocialBadge(kind="pypi", name=None)


def test_social_badge_requires_url_for_streamlit() -> None:
    with pytest.raises(ValueError, match="url is required"):
        SocialBadge(kind="streamlit", url=None)


def test_social_badge_accepts_github_name() -> None:
    b = SocialBadge(kind="github", name="org/repo")
    assert b.kind == "github"
    assert b.name == "org/repo"
