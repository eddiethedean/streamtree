"""Optional authentication helpers (``pip install \"streamtree[auth]\"``)."""

from __future__ import annotations

from typing import Any

from streamtree.elements.auth_gate import AuthGate

__all__ = ["AuthGate", "build_authenticator"]


def build_authenticator(config: dict[str, Any]) -> Any:
    """Construct ``streamlit_authenticator.Authenticate`` from a YAML-shaped dict.

    Expects at least ``credentials`` and ``cookie`` (with ``name``, ``key``, optional
    ``expiry_days``). Treat config as **trusted** input (same posture as app secrets).
    """
    try:
        cred = config["credentials"]
        cookie = config["cookie"]
        name = cookie["name"]
        key = cookie["key"]
    except KeyError as exc:
        key = exc.args[0] if exc.args else "?"
        msg = f"auth config missing required key: {key!r}"
        raise ValueError(msg) from exc
    days = float(cookie.get("expiry_days", 30.0))
    from streamlit_authenticator import Authenticate

    return Authenticate(credentials=cred, cookie_name=name, cookie_key=key, cookie_expiry_days=days)
