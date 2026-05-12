"""Theme model, context lookup, and optional CSS injection element."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from streamtree.app_context import lookup
from streamtree.core.element import Element

DEFAULT_THEME_KEY = "theme"

_HEX_COLOR = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


class Theme(BaseModel):
    """Serializable theme tokens for custom CSS (Streamlit-native config stays separate).

    ``primary_color`` and ``font_stack`` are validated as safe CSS tokens. ``custom_css`` is not
    sandboxed: treat it as **trusted** input (same privilege as app code writing ``<style>``).
    """

    model_config = {"frozen": True}

    primary_color: str = Field(
        default="#ff4b4b",
        description="Accent / link color: ``#RGB`` or ``#RRGGBB`` hex only.",
    )
    font_stack: str = Field(
        default="system-ui, -apple-system, Segoe UI, sans-serif",
        description="CSS font-family stack (no angle brackets or backticks).",
    )
    mode: Literal["light", "dark"] = "light"
    custom_css: str = Field(
        default="",
        description="Appended after generated tokens; trusted CSS only (no ``<script>``).",
    )

    @field_validator("primary_color")
    @classmethod
    def _primary_color_hex(cls, v: str) -> str:
        v = v.strip()
        if not _HEX_COLOR.fullmatch(v):
            raise ValueError("primary_color must be #RGB or #RRGGBB hex (e.g. #06c or #0066cc)")
        return v

    @field_validator("font_stack")
    @classmethod
    def _font_stack_chars(cls, v: str) -> str:
        v = v.strip()
        if any(ch in v for ch in "<>`"):
            raise ValueError("font_stack must not contain '<', '>', or '`'")
        return v

    @field_validator("custom_css")
    @classmethod
    def _custom_css_blocked_patterns(cls, v: str) -> str:
        low = v.lower()
        if "<script" in low or "expression(" in low:
            raise ValueError("custom_css contains disallowed patterns; keep Theme inputs trusted")
        return v


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
