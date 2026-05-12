"""Authentication gate element (renderer integrates ``streamtree.auth.build_authenticator``)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from streamtree.core.element import Element


@dataclass(frozen=True)
class AuthGate(Element):
    """Render ``streamlit-authenticator`` login; on success render ``child``."""

    config: dict[str, Any] = field(kw_only=True)
    child: Element = field(kw_only=True)
    login_location: Literal["main", "sidebar", "unrendered"] = field(default="main", kw_only=True)
    login_key: str = field(default="Login", kw_only=True)


__all__ = ["AuthGate"]
