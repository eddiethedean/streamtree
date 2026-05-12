"""Virtual element tree nodes."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any, TypeAlias


@dataclass(frozen=True)
class Element:
    """Base class for virtual tree nodes."""

    key: str | None = None


ElementChild: TypeAlias = Element | Sequence[Element | None] | None


@dataclass(frozen=True)
class Fragment(Element):
    """Group multiple children without a Streamlit container."""

    children: tuple[Element, ...] = field(default_factory=tuple)


def normalize_children(children: tuple[ElementChild, ...]) -> tuple[Element, ...]:
    out: list[Element] = []
    for ch in children:
        if ch is None:
            continue
        if isinstance(ch, Element):
            out.append(ch)
        elif isinstance(ch, Sequence) and not isinstance(ch, (str, bytes)):
            out.extend(normalize_children(tuple(ch)))  # type: ignore[arg-type]
        else:
            raise TypeError(f"Invalid child type: {type(ch)!r}")
    return tuple(out)


def fragment(*children: ElementChild, key: str | None = None) -> Fragment:
    return Fragment(key=key, children=normalize_children(children))


@dataclass(frozen=True)
class ComponentCall(Element):
    """Deferred invocation of a @component function."""

    fn: Callable[..., Element] = field(kw_only=True, repr=False)
    args: tuple[Any, ...] = field(default_factory=tuple, kw_only=True)
    kwargs: dict[str, Any] = field(default_factory=dict, kw_only=True)
