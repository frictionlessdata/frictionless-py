# TODO: rename into program
from __future__ import annotations
import sys
import typer
from typing import Optional
from .. import settings


# TODO: Rebase on Program.create? (see Server)


# Program


# TODO: remove this hack when Typer supports not-found commands catching
# https://github.com/tiangolo/typer/issues/18
class Program(typer.Typer):
    def __call__(self, *args, **kwargs):
        if len(sys.argv) >= 2 and sys.argv[1].count("."):
            sys.argv = [sys.argv[0], "summary", sys.argv[1]]
        return super().__call__(*args, **kwargs)


program = Program()


# Helpers


def version(value: bool):
    if value:
        typer.echo(settings.VERSION)
        raise typer.Exit()


# Command


@program.callback()
def program_main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version),
):
    """Describe, extract, validate and transform tabular data."""
    pass
