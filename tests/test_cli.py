"""Tests for the optional Typer CLI."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

import streamtree.cli as cli


def test_cli_doctor_prints_versions() -> None:
    runner = CliRunner()
    result = runner.invoke(cli._cli_app(), ["doctor"])
    assert result.exit_code == 0
    assert "streamtree" in result.stdout
    assert "streamlit" in result.stdout
    assert "python" in result.stdout
    assert "typer (cli extra) installed: True" in result.stdout


def test_cli_run_delegates_to_subprocess() -> None:
    runner = CliRunner()
    with patch("streamtree.helpers.runner.subprocess.run") as run:
        run.return_value = SimpleNamespace(returncode=0)
        result = runner.invoke(cli._cli_app(), ["run", "app.py", "--server.port", "9999"])
    assert result.exit_code == 0
    run.assert_called_once()
    cmd = run.call_args[0][0]
    assert cmd[-4:] == ["run", "app.py", "--server.port", "9999"]


def test_cli_run_no_script_args_exits_2() -> None:
    runner = CliRunner()
    result = runner.invoke(cli._cli_app(), ["run"])
    assert result.exit_code == 2


def test_cli_run_subprocess_filenotfound_exits_127() -> None:
    runner = CliRunner()
    with patch("streamtree.helpers.runner.subprocess.run", side_effect=FileNotFoundError):
        result = runner.invoke(cli._cli_app(), ["run", "missing.py"])
    assert result.exit_code == 127


def test_main_without_typer_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "_typer_spec", lambda: None)
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 1


def test_main_invokes_built_app(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = MagicMock()
    monkeypatch.setattr(cli, "_cli_app", lambda: fake)
    cli.main()
    fake.assert_called_once()
