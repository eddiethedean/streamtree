"""StreamTree: declarative, typed composition for Streamlit."""

from __future__ import annotations

from importlib.metadata import version as _package_version

__version__ = _package_version("streamtree")

from . import (
    app_context,
    asyncio,
    auth,
    charts,
    crud,
    elements,
    enterprise,
    forms,
    helpers,
    loading,
    perf,
    portals,
    routing,
    state,
    tables,
    testing,
)
from .app import App
from .core import (
    ComponentCall,
    Element,
    Fragment,
    component,
    debug_render_path,
    fragment,
    render,
    render_app,
)
from .theme import Theme, ThemeRoot, theme, theme_css

__all__ = [
    "App",
    "ComponentCall",
    "Element",
    "Fragment",
    "Theme",
    "ThemeRoot",
    "__version__",
    "app_context",
    "asyncio",
    "auth",
    "charts",
    "component",
    "crud",
    "debug_render_path",
    "elements",
    "enterprise",
    "forms",
    "fragment",
    "helpers",
    "loading",
    "perf",
    "portals",
    "render",
    "render_app",
    "routing",
    "state",
    "tables",
    "testing",
    "theme",
    "theme_css",
]
