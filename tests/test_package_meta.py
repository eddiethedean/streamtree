"""Package metadata exposed at import time."""

from __future__ import annotations

import streamtree


def test_version_matches_release_series() -> None:
    assert streamtree.__version__ == "0.10.0"


def test_public_exports_are_importable() -> None:
    """Guardrail: top-level ``__all__`` stays aligned with real attributes."""
    for name in streamtree.__all__:
        assert hasattr(streamtree, name), f"missing export: {name!r}"


def test_auth_submodule_exposed() -> None:
    assert hasattr(streamtree, "auth")
    assert hasattr(streamtree.auth, "AuthGate")
    assert hasattr(streamtree.auth, "build_authenticator")


def test_asyncio_and_forms_submodules_exposed() -> None:
    assert hasattr(streamtree.asyncio, "submit")
    assert hasattr(streamtree.asyncio, "dismiss_task")
    assert hasattr(streamtree.asyncio, "dismiss_tasks")
    assert hasattr(streamtree.asyncio, "submit_many")
    assert hasattr(streamtree.asyncio, "set_task_progress")
    assert hasattr(streamtree.asyncio, "is_task_cancel_requested")
    assert hasattr(streamtree.asyncio, "complete_cancelled")
    assert hasattr(streamtree.asyncio, "TaskHandle")
    assert hasattr(streamtree.forms, "bind_numeric_fields")
    assert hasattr(streamtree.forms, "number_inputs")
    assert hasattr(streamtree.forms, "NumericStateVar")
    assert hasattr(streamtree.forms, "bool_field_names")
    assert hasattr(streamtree.forms, "bind_bool_fields")


def test_loading_submodule_exposed() -> None:
    assert hasattr(streamtree, "loading")
    assert hasattr(streamtree.loading, "match_task")
    assert hasattr(streamtree.loading, "match_task_many")


def test_helpers_exports_page_links() -> None:
    assert hasattr(streamtree.helpers, "page_links")
    assert hasattr(streamtree.helpers, "prefetch_page_sources")
    assert hasattr(streamtree.helpers, "group_page_entries_by_order_prefix")
    assert hasattr(streamtree.helpers, "multipage_sidebar_nav")


def test_portals_submodule_exposed() -> None:
    assert hasattr(streamtree, "portals")
    assert hasattr(streamtree.portals, "gather_portals")
    assert hasattr(streamtree.portals, "portal_render_context")


def test_tables_and_charts_submodules_exposed() -> None:
    assert hasattr(streamtree, "tables")
    assert hasattr(streamtree.tables, "DataGrid")
    assert hasattr(streamtree, "charts")
    assert hasattr(streamtree.charts, "Chart")
    assert hasattr(streamtree.charts, "AltairChart")


def test_routing_query_helpers() -> None:
    assert hasattr(streamtree.routing, "sync_query_value")
    assert hasattr(streamtree.routing, "set_query_value")
    assert hasattr(streamtree.routing, "clear_query_param")
    assert hasattr(streamtree.routing, "clear_route")
    assert hasattr(streamtree.routing, "update_query_params")
