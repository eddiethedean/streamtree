"""Console entrypoint for ``streamtree`` (requires ``pip install 'streamtree[cli]'``)."""

from __future__ import annotations

import importlib.util
import sys

import click


def _typer_missing_message() -> str:
    return 'The streamtree CLI requires Typer. Install with:\n  pip install "streamtree[cli]"\n'


def _typer_spec():
    """Return ``importlib.util.find_spec('typer')`` (hookable for tests)."""
    return importlib.util.find_spec("typer")


def _cli_app():
    import typer

    from streamtree import __version__
    from streamtree.helpers.runner import run_streamlit_sync

    app = typer.Typer(help="StreamTree developer commands.", no_args_is_help=True)

    @app.command(
        "run",
        context_settings={
            "allow_extra_args": True,
            "ignore_unknown_options": True,
        },
    )
    def run_cmd(ctx: click.Context) -> None:
        """Forward to ``python -m streamlit run`` (same cwd; exit code preserved)."""
        code = run_streamlit_sync(ctx.args)
        raise typer.Exit(code)

    @app.command("doctor")
    def doctor_cmd() -> None:
        """Print StreamTree, Streamlit, Python, and optional CLI dependency versions."""
        import streamlit

        typer.echo(f"streamtree {__version__}")
        typer.echo(f"streamlit {streamlit.__version__}")
        typer.echo(f"python {sys.version.split()[0]}")
        typer_installed = importlib.util.find_spec("typer") is not None
        typer.echo(f"typer (cli extra) installed: {typer_installed}")

    return app


def main() -> None:
    """``streamtree`` script: ``streamtree <subcommand> …``."""
    if _typer_spec() is None:
        sys.stderr.write(_typer_missing_message())
        raise SystemExit(1)
    app = _cli_app()
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
