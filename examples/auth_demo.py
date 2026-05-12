"""Demo: optional login gate (requires ``pip install \"streamtree[auth]\"``).

Replace ``AUTH_CONFIG`` with a real **streamlit-authenticator** YAML-shaped dict
(credentials + cookie). Treat it as **trusted secrets** (same posture as API keys).
See https://github.com/mkhorasani/Streamlit-Authenticator for hashing passwords and
full config layout. This file is a structural example only.
"""

from __future__ import annotations

from streamtree import component, render_app
from streamtree.app import App
from streamtree.auth import AuthGate
from streamtree.elements import Page, Text, VStack

# Minimal shape only — replace before use in production.
AUTH_CONFIG: dict = {
    "credentials": {"usernames": {}},
    "cookie": {"name": "streamtree_auth", "key": "change_this_random_secret", "expiry_days": 30},
}


@component
def Protected() -> object:
    return Page(VStack(Text("You are signed in (example).")))


if __name__ == "__main__":
    render_app(App(page_title="Auth demo", body=AuthGate(config=AUTH_CONFIG, child=Protected())))
