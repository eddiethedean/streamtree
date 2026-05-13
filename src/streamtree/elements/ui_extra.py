"""Optional ``streamlit-extras`` wrappers (``pip install \"streamtree[ui]\"``)."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, Literal

from streamtree.core.element import Element, ElementChild, normalize_children

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
class BottomDock(Element):
    """Pin children to the bottom main area via ``streamlit_extras.bottom_container.bottom``."""

    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(self, *children: ElementChild, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class FloatingActionButton(Element):
    """Floating action button via ``streamlit_extras.floating_button.floating_button``."""

    label: str = ""
    help: str | None = field(default=None, kw_only=True)
    on_click: Callable[..., None] | None = field(default=None, kw_only=True)
    on_click_args: tuple[Any, ...] | None = field(default=None, kw_only=True)
    on_click_kwargs: dict[str, Any] | None = field(default=None, kw_only=True)
    button_type: Literal["primary", "secondary"] = field(default="secondary", kw_only=True)
    icon: str | None = field(default=None, kw_only=True)
    disabled: bool = field(default=False, kw_only=True)

    def __init__(
        self,
        label: str,
        *,
        help: str | None = None,
        on_click: Callable[..., None] | None = None,
        on_click_args: tuple[Any, ...] | None = None,
        on_click_kwargs: dict[str, Any] | None = None,
        button_type: Literal["primary", "secondary"] = "secondary",
        icon: str | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "help", help)
        object.__setattr__(self, "on_click", on_click)
        object.__setattr__(self, "on_click_args", on_click_args)
        object.__setattr__(self, "on_click_kwargs", on_click_kwargs)
        object.__setattr__(self, "button_type", button_type)
        object.__setattr__(self, "icon", icon)
        object.__setattr__(self, "disabled", disabled)


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


@dataclass(frozen=True)
class Stoggle(Element):
    """Expandable summary/content via ``streamlit_extras.stoggle.stoggle``."""

    summary: str = ""
    content: str = ""

    def __init__(self, summary: str, content: str, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "summary", summary)
        object.__setattr__(self, "content", content)


@dataclass(frozen=True)
class TaggerRow(Element):
    """Tag row via ``streamlit_extras.tags.tagger_component``."""

    content: str = ""
    tags: tuple[str, ...] = field(default_factory=tuple)
    color_name: str | tuple[str, ...] | None = field(default=None, kw_only=True)
    text_color_name: str | tuple[str, ...] | None = field(default=None, kw_only=True)

    def __init__(
        self,
        content: str,
        tags: Sequence[str],
        *,
        color_name: str | tuple[str, ...] | None = None,
        text_color_name: str | tuple[str, ...] | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "tags", tuple(tags))
        object.__setattr__(self, "color_name", color_name)
        object.__setattr__(self, "text_color_name", text_color_name)


@dataclass(frozen=True)
class MentionChip(Element):
    """External link chip via ``streamlit_extras.mention.mention``."""

    label: str = ""
    url: str = ""
    icon: str = field(default="🔗", kw_only=True)

    def __init__(
        self,
        label: str,
        url: str,
        *,
        icon: str = "🔗",
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "url", url)
        object.__setattr__(self, "icon", icon)


__all__ = [
    "BottomDock",
    "ColoredHeader",
    "ColoredHeaderColor",
    "FloatingActionButton",
    "MentionChip",
    "SocialBadge",
    "SocialBadgeKind",
    "Stoggle",
    "StyleMetricCards",
    "TaggerRow",
    "VerticalSpaceLines",
]
