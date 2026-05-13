"""Console entrypoint for ``streamtree`` (requires ``pip install 'streamtree[cli]'``)."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import click


def _typer_missing_message() -> str:
    return 'The streamtree CLI requires Typer. Install with:\n  pip install "streamtree[cli]"\n'


def _typer_spec():
    """Return ``importlib.util.find_spec('typer')`` (hookable for tests)."""
    return importlib.util.find_spec("typer")


def _cli_app():
    import typer
    from streamlit.runtime import exists as streamlit_runtime_exists

    from streamtree import __version__
    from streamtree.helpers.runner import run_streamlit_sync
    from streamtree.helpers.scaffold import write_init_project
    from streamtree.helpers.tree_target import load_element_from_target
    from streamtree.testing import render_to_tree, summarize_tree_kinds
    from streamtree.testing.viz import format_tree_text, tree_dict_to_mermaid

    app = typer.Typer(help="StreamTree developer commands.", no_args_is_help=True)

    def _run_streamlit(ctx: click.Context) -> None:
        code = run_streamlit_sync(ctx.args)
        raise typer.Exit(code)

    _streamlit_forward_ctx = {
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    }

    @app.command("run", context_settings=_streamlit_forward_ctx)
    def run_cmd(ctx: click.Context) -> None:
        """Forward to ``python -m streamlit run`` (same cwd; exit code preserved)."""
        _run_streamlit(ctx)

    @app.command("preview", context_settings=_streamlit_forward_ctx)
    def preview_cmd(ctx: click.Context) -> None:
        """Alias for ``run`` (same Streamlit forwarding). Use ``streamtree tree`` for static structure."""
        _run_streamlit(ctx)

    @app.command("serve", context_settings=_streamlit_forward_ctx)
    def serve_cmd(ctx: click.Context) -> None:
        """Alias for ``run`` (optional StreamTree-shaped entry to Streamlit's server)."""
        _run_streamlit(ctx)

    @app.command("doctor")
    def doctor_cmd(
        *,
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Print introspection pointers and whether a Streamlit runtime is active.",
        ),
    ) -> None:
        """Print StreamTree, Streamlit, Python, and optional CLI dependency versions."""
        import streamlit

        typer.echo(f"streamtree {__version__}")
        typer.echo(f"streamlit {streamlit.__version__}")
        typer.echo(f"python {sys.version.split()[0]}")
        typer_installed = importlib.util.find_spec("typer") is not None
        typer.echo(f"typer (cli extra) installed: {typer_installed}")
        if verbose:
            rt = streamlit_runtime_exists()
            typer.echo(f"streamlit runtime active: {rt}")
            typer.echo(
                "Dev introspection: ``from streamtree import debug_render_path``; "
                "``streamtree.testing.introspection``; ``streamtree.asyncio.summarize_async_tasks``."
            )

    @app.command("tree")
    def tree_cmd(
        target: str = typer.Argument(
            ...,
            help="``module:attr`` — Element instance or zero-arg callable returning Element",
        ),
        *,
        expand_components: bool = typer.Option(
            False,
            "--expand-components",
            help="Expand @component nodes (requires an active Streamlit runtime / session).",
        ),
        output_format: str = typer.Option(
            "json",
            "--format",
            "-f",
            help="json | text | mermaid (ignored when using --summarize).",
        ),
        summarize: bool = typer.Option(
            False,
            "--summarize",
            help="Print JSON object of element kind counts instead of the full tree.",
        ),
    ) -> None:
        """Print a JSON/text/Mermaid view of the element tree for ``module:attr``."""
        if expand_components and not streamlit_runtime_exists():
            typer.echo(
                "``--expand-components`` requires an active Streamlit session "
                "(for example inside ``streamlit run``).",
                err=True,
            )
            raise typer.Exit(1)
        try:
            root = load_element_from_target(target)
        except (ValueError, TypeError) as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
        from streamtree.core.context import render_context

        if expand_components:
            with render_context("cli-tree"):
                tree = render_to_tree(root, expand_components=True)
        else:
            tree = render_to_tree(root, expand_components=False)
        if summarize:
            typer.echo(json.dumps(summarize_tree_kinds(tree), indent=2, sort_keys=True))
            return
        fmt = output_format.strip().lower()
        if fmt == "json":
            typer.echo(json.dumps(tree, indent=2, sort_keys=True))
        elif fmt == "text":
            typer.echo(format_tree_text(tree))
        elif fmt == "mermaid":
            typer.echo(tree_dict_to_mermaid(tree))
        else:
            typer.echo(
                f"Unknown --format {output_format!r} (use json, text, or mermaid).", err=True
            )
            raise typer.Exit(1)

    @app.command("init")
    def init_cmd(
        path: Path | None = typer.Argument(
            default=None,
            help="Directory to write into (default: current directory)",
        ),
        *,
        name: str = typer.Option("StreamTree app", help="App page title / window name"),
        with_pages: bool = typer.Option(
            False,
            help="Also create ``pages/`` with a sample page script",
        ),
        force: bool = typer.Option(False, help="Overwrite existing generated files"),
        template: str = typer.Option(
            "default",
            "--template",
            "-t",
            help="app.py template: default | crud | explore | enterprise",
        ),
    ) -> None:
        """Scaffold ``app.py`` (and optional ``pages/``) for ``streamtree run``."""
        root = Path.cwd() if path is None else path
        try:
            written = write_init_project(
                root,
                page_title=name,
                with_pages=with_pages,
                force=force,
                template=template,
            )
        except FileExistsError as exc:
            typer.echo(f"Refusing to overwrite (use --force): {exc}", err=True)
            raise typer.Exit(1) from exc
        except ValueError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(1) from exc
        for p in written:
            typer.echo(f"Wrote {p.resolve()}")

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
