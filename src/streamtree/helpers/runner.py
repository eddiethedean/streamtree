"""Argv and subprocess helpers for delegating to ``streamlit run``."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence


def build_streamlit_run_argv(forwarded: Sequence[str]) -> list[str]:
    """Build argv for ``python -m streamlit run …`` with ``forwarded`` args after ``run``."""
    return [sys.executable, "-m", "streamlit", "run", *forwarded]


def run_streamlit_sync(forwarded: Sequence[str]) -> int:
    """Run Streamlit in a subprocess; return its exit code (``2`` if no script args).

    On missing interpreter / ``streamlit`` module entrypoint failures that surface as
    :exc:`FileNotFoundError` from :func:`subprocess.run`, returns ``127``.
    """
    args = list(forwarded)
    if not args:
        return 2
    cmd = build_streamlit_run_argv(args)
    try:
        completed = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        return 127
    return int(completed.returncode)


__all__ = ["build_streamlit_run_argv", "run_streamlit_sync"]
