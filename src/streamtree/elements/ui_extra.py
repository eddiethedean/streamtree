"""Optional ``streamlit-extras`` wrappers (``pip install \"streamtree[ui]\"``)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from streamtree.core.element import Element

ColoredHeaderColor = Literal[
    "light-blue-70",
    "orange-70",
    "blue-green-70",
    "blue-70",
    "violet-70",
    "red-70",
    "green-70",
    "yellow-80",
]

SocialBadgeKind = Literal["pypi", "github", "streamlit", "twitter", "buymeacoffee"]


@dataclass(frozen=True)
class ColoredHeader(Element):
    """Themed section header via ``streamlit_extras.colored_header``."""

    label: str = ""
    description: str = ""
    color_name: ColoredHeaderColor = "blue-70"

    def __init__(
        self,
        label: str,
        *,
        description: str = "",
        color_name: ColoredHeaderColor = "blue-70",
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "description", description)
        object.__setattr__(self, "color_name", color_name)


@dataclass(frozen=True)
class VerticalSpaceLines(Element):
    """Insert blank lines via ``streamlit_extras.add_vertical_space``."""

    num_lines: int = 1

    def __init__(self, num_lines: int = 1, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "num_lines", max(1, num_lines))


@dataclass(frozen=True)
class SocialBadge(Element):
    """Platform badge row via ``streamlit_extras.badges.badge`` (PyPI, GitHub, etc.)."""

    kind: SocialBadgeKind = field(kw_only=True)
    name: str | None = field(default=None, kw_only=True)
    url: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if self.kind in ("pypi", "github", "twitter", "buymeacoffee"):
            if not (self.name and str(self.name).strip()):
                raise ValueError("name is required for this badge kind")
        if self.kind == "streamlit" and not (self.url and str(self.url).strip()):
            raise ValueError("url is required for streamlit badge kind")


@dataclass(frozen=True)
class StyleMetricCards(Element):
    """Apply ``streamlit_extras.metric_cards.style_metric_cards`` CSS to ``st.metric`` tiles."""

    background_color: str | None = field(default=None, kw_only=True)
    border_size_px: int = field(default=1, kw_only=True)
    border_color: str | None = field(default=None, kw_only=True)
    border_radius_px: int = field(default=5, kw_only=True)
    border_left_color: str = field(default="#9AD8E1", kw_only=True)
    box_shadow: bool = field(default=True, kw_only=True)


__all__ = [
    "ColoredHeader",
    "ColoredHeaderColor",
    "SocialBadge",
    "SocialBadgeKind",
    "StyleMetricCards",
    "VerticalSpaceLines",
]
