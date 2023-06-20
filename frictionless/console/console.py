from __future__ import annotations

import sys
from typing import Any, Optional

import typer

from .. import settings

# TODO: Rebase on Console.create? (see Server)


# Console


# TODO: remove this hack when Typer supports not-found commands catching
# https://github.com/tiangolo/typer/issues/18
class Console(typer.Typer):
    def __call__(self, *args: Any, **kwargs: Any):
        if len(sys.argv) >= 2 and sys.argv[1].count("."):
            sys.argv = [sys.argv[0], "summary", sys.argv[1]]
        return super().__call__(*args, **kwargs)


console = Console()


# Helpers


def version(value: bool):
    if value:
        typer.echo(settings.VERSION)
        raise typer.Exit()


# Command


@console.callback()
def console_main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version),
):
    """Describe, extract, validate and transform tabular data."""
    pass
