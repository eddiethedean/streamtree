"""Layout primitives."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from streamtree.core.element import Element, ElementChild, normalize_children
from streamtree.state import StateVar, ToggleState


@dataclass(frozen=True)
class VStack(Element):
    """Render children vertically in order."""

    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(self, *children: ElementChild, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class HStack(Element):
    """Render children in a horizontal row of equal columns.

    When ``gap`` is a non-empty string (e.g. ``\"12px\"`` or ``\"0.5rem\"``), narrow gutter columns
    are inserted between children; each gutter uses the string as CSS ``min-width`` on a spacer.
    """

    children: tuple[Element, ...] = field(default_factory=tuple)
    gap: str | None = None

    def __init__(
        self,
        *children: ElementChild,
        gap: str | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "gap", gap)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Columns(Element):
    """Render children in weighted columns (``weights`` length must match children)."""

    children: tuple[Element, ...] = field(default_factory=tuple)
    weights: tuple[float, ...] = field(default_factory=tuple)

    def __init__(
        self,
        *children: ElementChild,
        weights: tuple[float, ...] | None = None,
        key: str | None = None,
    ) -> None:
        ch = normalize_children(children)
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", ch)
        if weights is None:
            object.__setattr__(self, "weights", tuple(1.0 for _ in ch))
        else:
            if len(weights) != len(ch):
                raise ValueError(
                    f"Columns weights length ({len(weights)}) must match children ({len(ch)})"
                )
            object.__setattr__(self, "weights", weights)


@dataclass(frozen=True)
class Grid(Element):
    """Render children left-to-right in a fixed column count."""

    children: tuple[Element, ...] = field(default_factory=tuple)
    columns: int = 2

    def __init__(self, *children: ElementChild, columns: int = 2, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "columns", max(1, columns))
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Card(Element):
    """Group content in a bordered container when supported by Streamlit."""

    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(self, *children: ElementChild, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Page(Element):
    """Top-level page container (column layout)."""

    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(self, *children: ElementChild, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Tabs(Element):
    """Named tabs; each entry is (title, child_element)."""

    tabs: tuple[tuple[str, Element], ...] = ()

    def __init__(self, *tabs: tuple[str, Element], key: str | None = None) -> None:
        if not tabs:
            raise ValueError("Tabs requires at least one (title, child) pair")
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "tabs", tabs)


@dataclass(frozen=True)
class Sidebar(Element):
    """Render children in ``st.sidebar``."""

    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(self, *children: ElementChild, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Form(Element):
    """Streamlit form boundary."""

    form_key: str = "form"
    clear_on_submit: bool = False
    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(
        self,
        *children: ElementChild,
        form_key: str = "form",
        clear_on_submit: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "form_key", form_key)
        object.__setattr__(self, "clear_on_submit", clear_on_submit)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Expander(Element):
    """Collapsible section."""

    label: str = ""
    expanded: bool = False
    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(
        self,
        label: str,
        *children: ElementChild,
        expanded: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "expanded", expanded)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Spacer(Element):
    """Vertical breathing room."""

    height: int | None = None


DialogOpen = bool | StateVar[bool] | ToggleState


@dataclass(frozen=True)
class Dialog(Element):
    """Modal dialog when ``open`` is true (Streamlit ``st.dialog``; Streamlit **≥ 1.33**).

    On Streamlit versions **without** ``st.dialog``, the renderer shows a warning and
    draws the dialog **children inline** on the main page (not a modal). Prefer upgrading
    Streamlit for true dialog behavior; :class:`Popover` falls back to an expander instead.
    """

    title: str = ""
    open: DialogOpen = False
    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(
        self,
        title: str,
        *children: ElementChild,
        open: DialogOpen = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "open", open)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class Popover(Element):
    """Trigger + panel (``st.popover`` when available; falls back to expander)."""

    label: str = ""
    disabled: bool = False
    children: tuple[Element, ...] = field(default_factory=tuple)

    def __init__(
        self,
        label: str,
        *children: ElementChild,
        disabled: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "disabled", disabled)
        object.__setattr__(self, "children", normalize_children(children))


@dataclass(frozen=True)
class ErrorBoundary(Element):
    """Render ``child``; on exception render ``fallback`` instead.

    If ``on_error`` is set, it is invoked with the caught exception before ``fallback``
    is rendered. Callbacks **must not raise**; if they do, the error is logged and
    ``fallback`` is still shown.
    """

    child: Element = field(kw_only=True)
    fallback: Element = field(kw_only=True)
    on_error: Callable[[Exception], None] | None = field(default=None, kw_only=True)


@dataclass(frozen=True)
class Routes(Element):
    """Render exactly one child tree based on :func:`streamtree.routing.sync_route`."""

    routes: tuple[tuple[str, Element], ...] = field(kw_only=True)
    default: str = "home"
    query_param: str = "route"

    def __post_init__(self) -> None:
        if not self.routes:
            raise ValueError("Routes requires at least one (name, element) pair")
        names = [n for n, _ in self.routes]
        if len(set(names)) != len(names):
            raise ValueError("Routes route names must be unique")
        qp = self.query_param.strip() if isinstance(self.query_param, str) else ""
        if not qp:
            raise ValueError("Routes.query_param must be a non-empty string")
        dflt = self.default.strip() if isinstance(self.default, str) else ""
        if not dflt:
            raise ValueError("Routes.default must be a non-empty string")
        route_names = {n for n, _ in self.routes}
        if dflt not in route_names:
            raise ValueError(
                f"Routes.default {dflt!r} must match a route name; got {sorted(route_names)!r}"
            )
        object.__setattr__(self, "query_param", qp)
        object.__setattr__(self, "default", dflt)
