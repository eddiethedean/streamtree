"""Theme model, context lookup, and optional CSS injection element."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

from streamtree.app_context import lookup
from streamtree.core.element import Element

DEFAULT_THEME_KEY = "theme"


class Theme(BaseModel):
    """Serializable theme tokens for custom CSS (Streamlit-native config stays separate)."""

    model_config = {"frozen": True}

    primary_color: str = Field(default="#ff4b4b", description="Accent / link color")
    font_stack: str = Field(
        default="system-ui, -apple-system, Segoe UI, sans-serif",
        description="CSS font-family stack",
    )
    mode: Literal["light", "dark"] = "light"
    custom_css: str = Field(default="", description="Appended after generated tokens")


def theme(*, default: Theme | None = None) -> Theme:
    """Resolve ``Theme`` from ``provider(theme=...)`` or fall back to ``default`` / built-in."""
    raw = lookup(DEFAULT_THEME_KEY, default)
    if isinstance(raw, Theme):
        return raw
    if default is not None:
        return default
    return Theme()


def theme_css(t: Theme | None = None) -> str:
    """Build a small ``<style>`` body from ``Theme`` (no outer tags)."""
    m = t or theme()
    base = (
        f":root {{ --st-theme-primary: {m.primary_color}; "
        f"--st-font-sans: {m.font_stack}; "
        f"color-scheme: {m.mode}; }}\n"
        f"html, body, [data-testid='stAppViewContainer'] "
        f"{{ font-family: var(--st-font-sans); }}\n"
    )
    return base + (m.custom_css.strip() + "\n" if m.custom_css.strip() else "")


@dataclass(frozen=True)
class ThemeRoot(Element):
    """Virtual node that injects CSS from :func:`theme` / ``provider(theme=...)``."""

    def __init__(self, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)


__all__ = [
    "DEFAULT_THEME_KEY",
    "Theme",
    "ThemeRoot",
    "theme",
    "theme_css",
]
