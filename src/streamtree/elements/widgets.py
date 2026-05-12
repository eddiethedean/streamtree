"""Leaf widgets and controls."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from streamtree.core.element import Element
from streamtree.state import FormState, StateVar, ToggleState

NumberValue = (
    int
    | float
    | StateVar[int]
    | StateVar[float]
    | StateVar[int | None]
    | StateVar[float | None]
    | FormState[int]
    | FormState[float]
    | FormState[int | None]
    | FormState[float | None]
    | None
)


@dataclass(frozen=True)
class Text(Element):
    body: str = ""

    def __init__(self, body: str, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "body", body)


@dataclass(frozen=True)
class Markdown(Element):
    body: str = ""
    unsafe_allow_html: bool = False

    def __init__(
        self,
        body: str,
        *,
        unsafe_allow_html: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "body", body)
        object.__setattr__(self, "unsafe_allow_html", unsafe_allow_html)


@dataclass(frozen=True)
class Button(Element):
    label: str = ""
    on_click: Callable[[], None] | None = None
    disabled: bool = False
    submit: bool = False
    help: str | None = None

    def __init__(
        self,
        label: str,
        *,
        on_click: Callable[[], None] | None = None,
        disabled: bool = False,
        submit: bool = False,
        help: str | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "on_click", on_click)
        object.__setattr__(self, "disabled", disabled)
        object.__setattr__(self, "submit", submit)
        object.__setattr__(self, "help", help)


@dataclass(frozen=True)
class TextInput(Element):
    label: str = ""
    value: str | StateVar[str] | FormState[str] | None = None
    placeholder: str | None = None
    disabled: bool = False
    type: Literal["default", "password"] = "default"

    def __init__(
        self,
        label: str,
        *,
        value: str | StateVar[str] | FormState[str] | None = None,
        placeholder: str | None = None,
        disabled: bool = False,
        type: Literal["default", "password"] = "default",
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "placeholder", placeholder)
        object.__setattr__(self, "disabled", disabled)
        object.__setattr__(self, "type", type)


@dataclass(frozen=True)
class NumberInput(Element):
    label: str = ""
    value: NumberValue = None
    min_value: int | float | None = None
    max_value: int | float | None = None
    step: int | float | None = None
    format: str | None = None
    disabled: bool = False

    def __init__(
        self,
        label: str,
        *,
        value: NumberValue = None,
        min_value: int | float | None = None,
        max_value: int | float | None = None,
        step: int | float | None = None,
        format: str | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "min_value", min_value)
        object.__setattr__(self, "max_value", max_value)
        object.__setattr__(self, "step", step)
        object.__setattr__(self, "format", format)
        object.__setattr__(self, "disabled", disabled)


@dataclass(frozen=True)
class PageLink(Element):
    """Multipage navigation via ``st.page_link`` (Streamlit ≥ 1.30)."""

    label: str = ""
    page: str = ""
    icon: str | None = None
    help: str | None = None
    disabled: bool = False
    use_container_width: bool | None = None

    def __init__(
        self,
        label: str,
        *,
        page: str,
        icon: str | None = None,
        help: str | None = None,
        disabled: bool = False,
        use_container_width: bool | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "page", page)
        object.__setattr__(self, "icon", icon)
        object.__setattr__(self, "help", help)
        object.__setattr__(self, "disabled", disabled)
        object.__setattr__(self, "use_container_width", use_container_width)


@dataclass(frozen=True)
class Selectbox(Element):
    label: str = ""
    options: Sequence[Any] = ()
    index: int | StateVar[int] | None = None
    format_func: Callable[[Any], str] | None = None
    disabled: bool = False

    def __init__(
        self,
        label: str,
        *,
        options: Sequence[Any],
        index: int | StateVar[int] | None = 0,
        format_func: Callable[[Any], str] | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "options", tuple(options))
        object.__setattr__(self, "index", index)
        object.__setattr__(self, "format_func", format_func)
        object.__setattr__(self, "disabled", disabled)


@dataclass(frozen=True)
class Checkbox(Element):
    label: str = ""
    value: bool | StateVar[bool] | ToggleState | None = None
    disabled: bool = False

    def __init__(
        self,
        label: str,
        *,
        value: bool | StateVar[bool] | ToggleState | None = None,
        disabled: bool = False,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "disabled", disabled)


@dataclass(frozen=True)
class DataFrame(Element):
    data: Any = None
    width: int | None = None
    height: int | None = None

    def __init__(
        self,
        data: Any,
        *,
        width: int | None = None,
        height: int | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "height", height)


@dataclass(frozen=True)
class Image(Element):
    image: Any = None
    caption: str | None = None
    width: int | None = None
    use_column_width: bool | Literal["auto", "always", "never"] | None = None
    use_container_width: bool | None = None

    def __init__(
        self,
        image: Any,
        *,
        caption: str | None = None,
        width: int | None = None,
        use_column_width: bool | Literal["auto", "always", "never"] | None = None,
        use_container_width: bool | None = None,
        key: str | None = None,
    ) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "image", image)
        object.__setattr__(self, "caption", caption)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "use_column_width", use_column_width)
        object.__setattr__(self, "use_container_width", use_container_width)


@dataclass(frozen=True)
class Divider(Element):
    """Horizontal rule."""

    def __init__(self, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)


@dataclass(frozen=True)
class Title(Element):
    text: str = ""

    def __init__(self, text: str, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "text", text)


@dataclass(frozen=True)
class Subheader(Element):
    text: str = ""

    def __init__(self, text: str, *, key: str | None = None) -> None:
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "text", text)
