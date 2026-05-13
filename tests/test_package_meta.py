"""Package metadata exposed at import time."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import streamtree


def _line_scan_project_version(text: str) -> str:
    """Parse ``[project].version`` without tomllib (Python 3.10 CI path)."""
    in_project = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line == "[project]":
            in_project = True
            continue
        if in_project and line.startswith("[") and line.endswith("]"):
            break
        if in_project and line.startswith("version"):
            _, _, rhs = line.partition("=")
            return rhs.strip().strip('"').strip("'")
    raise AssertionError("pyproject.toml missing [project].version")


def _pyproject_project_version() -> str:
    root = Path(__file__).resolve().parents[1]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    if sys.version_info >= (3, 11):
        import tomllib

        return tomllib.loads(text)["project"]["version"]
    return _line_scan_project_version(text)


def test_version_matches_pyproject() -> None:
    assert streamtree.__version__ == _pyproject_project_version()


def test_version_matches_importlib_distribution() -> None:
    """``__init__`` reads ``importlib.metadata.version``; guard against drift."""
    from importlib.metadata import version

    assert streamtree.__version__ == version("streamtree")


@pytest.mark.skipif(sys.version_info < (3, 11), reason="tomllib is stdlib baseline for comparison")
def test_pyproject_line_scan_matches_tomllib() -> None:
    """Keep the 3.10 line parser aligned with real TOML parsing."""
    import tomllib

    root = Path(__file__).resolve().parents[1]
    text = (root / "pyproject.toml").read_text(encoding="utf-8")
    assert _line_scan_project_version(text) == tomllib.loads(text)["project"]["version"]


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
    assert hasattr(streamtree.asyncio, "summarize_async_tasks")
    assert hasattr(streamtree.forms, "bind_numeric_fields")
    assert hasattr(streamtree.forms, "number_inputs")
    assert hasattr(streamtree.forms, "NumericStateVar")
    assert hasattr(streamtree.forms, "bool_field_names")
    assert hasattr(streamtree.forms, "bind_bool_fields")


def test_loading_submodule_exposed() -> None:
    assert hasattr(streamtree, "loading")
    assert hasattr(streamtree.loading, "match_task")
    assert hasattr(streamtree.loading, "match_task_many")
    assert hasattr(streamtree.loading, "submit_many_ordered")


def test_phase3_submodules_exposed() -> None:
    assert hasattr(streamtree, "crud")
    assert hasattr(streamtree.crud, "save_intent_counter")
    assert hasattr(streamtree, "enterprise")
    assert hasattr(streamtree.enterprise, "emit_event")
    assert hasattr(streamtree, "perf")
    assert hasattr(streamtree.perf, "perf_bump")


def test_helpers_explore_exports() -> None:
    assert hasattr(streamtree.helpers, "column_summary")
    assert hasattr(streamtree.helpers, "dataframe_profile")


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
    assert hasattr(streamtree.charts, "EChartsChart")


def test_routing_query_helpers() -> None:
    assert hasattr(streamtree.routing, "sync_query_value")
    assert hasattr(streamtree.routing, "set_query_value")
    assert hasattr(streamtree.routing, "clear_query_param")
    assert hasattr(streamtree.routing, "clear_route")
    assert hasattr(streamtree.routing, "update_query_params")
