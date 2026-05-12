"""Tests for streamtree.theme."""

from __future__ import annotations

from streamtree.app_context import provider
from streamtree.testing import render_to_tree
from streamtree.theme import Theme, ThemeRoot, theme, theme_css


def test_theme_css_contains_tokens() -> None:
    css = theme_css(Theme(primary_color="#00ff00", mode="dark"))
    assert "#00ff00" in css
    assert "color-scheme: dark" in css


def test_theme_from_provider() -> None:
    t = Theme(primary_color="#111111")
    with provider(theme=t):
        assert theme().primary_color == "#111111"


def test_theme_default_when_missing() -> None:
    assert theme().primary_color == Theme().primary_color


def test_theme_default_when_lookup_wrong_type() -> None:
    fallback = Theme(primary_color="#010101")
    with provider(theme="not-a-theme"):  # type: ignore[arg-type]
        assert theme(default=fallback) is fallback


def test_theme_wrong_type_without_default_returns_builtin() -> None:
    with provider(theme=object()):  # type: ignore[arg-type]
        assert theme() == Theme()


def test_theme_css_none_argument_uses_resolved_theme() -> None:
    css = theme_css(None)
    assert "color-scheme: light" in css
    assert "--st-theme-primary" in css


def test_theme_css_appends_custom_css() -> None:
    css = theme_css(Theme(custom_css="body { margin: 0; }"))
    assert "margin: 0" in css


def test_theme_css_ignores_whitespace_only_custom_css() -> None:
    css = theme_css(Theme(custom_css="  \n\t  "))
    assert "color-scheme" in css
    assert "margin" not in css


def test_render_to_tree_theme_root() -> None:
    tree = render_to_tree(ThemeRoot())
    assert tree == {"kind": "ThemeRoot", "key": None}


def test_render_to_tree_theme_root_with_key() -> None:
    tree = render_to_tree(ThemeRoot(key="layout"))
    assert tree == {"kind": "ThemeRoot", "key": "layout"}
