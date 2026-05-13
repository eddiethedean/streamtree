"""Optional integration helpers (stdlib-first where possible)."""

from streamtree.helpers.pages import (
    PageEntry,
    discover_pages,
    group_page_entries_by_order_prefix,
    iter_page_entries,
    list_page_entries,
    multipage_sidebar_nav,
    page_links,
    page_links_sidebar_sections,
    pages_dir_next_to,
    prefetch_page_sources,
)
from streamtree.helpers.runner import build_streamlit_run_argv, run_streamlit_sync

__all__ = [
    "PageEntry",
    "build_streamlit_run_argv",
    "discover_pages",
    "group_page_entries_by_order_prefix",
    "iter_page_entries",
    "list_page_entries",
    "multipage_sidebar_nav",
    "page_links",
    "page_links_sidebar_sections",
    "pages_dir_next_to",
    "prefetch_page_sources",
    "run_streamlit_sync",
]
