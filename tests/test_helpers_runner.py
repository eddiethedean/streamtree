"""Tests for ``streamtree.helpers.runner``."""

from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest.mock import patch

from streamtree.helpers.runner import build_streamlit_run_argv, run_streamlit_sync


def test_build_streamlit_run_argv_includes_streamlit_run() -> None:
    argv = build_streamlit_run_argv(["examples/counter.py", "--", "--server.headless", "true"])
    assert argv[0] == sys.executable
    assert argv[1:4] == ["-m", "streamlit", "run"]
    assert argv[4:] == ["examples/counter.py", "--", "--server.headless", "true"]


def test_run_streamlit_sync_empty_args_returns_2() -> None:
    assert run_streamlit_sync([]) == 2


def test_run_streamlit_sync_returns_subprocess_code() -> None:
    with patch("streamtree.helpers.runner.subprocess.run") as run:
        run.return_value = SimpleNamespace(returncode=42)
        assert run_streamlit_sync(["x.py"]) == 42
    run.assert_called_once()
    cmd = run.call_args[0][0]
    assert "streamlit" in cmd


def test_run_streamlit_sync_filenotfound_returns_127() -> None:
    with patch("streamtree.helpers.runner.subprocess.run", side_effect=FileNotFoundError):
        assert run_streamlit_sync(["x.py"]) == 127
