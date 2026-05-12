"""Optional ``streamlit-extras`` wrappers (``pip install \"streamtree[ui]\"``)."""

from __future__ import annotations

from dataclasses import dataclass
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


__all__ = ["ColoredHeader", "ColoredHeaderColor", "VerticalSpaceLines"]
