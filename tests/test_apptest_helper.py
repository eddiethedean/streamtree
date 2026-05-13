"""Tests for ``streamtree.testing.apptest``."""

from __future__ import annotations

import streamlit as st

from streamtree.testing.apptest import run_app_function


def _tiny_app() -> None:
    st.write("apptest-helper")


def test_run_app_function_executes() -> None:
    at = run_app_function(_tiny_app, timeout=25)
    assert at is not None
