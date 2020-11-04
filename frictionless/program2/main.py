import typer
from typing import Optional
from .. import config


# Program

program = typer.Typer()


# Helpers


def version(value: bool):
    if value:
        typer.echo(config.VERSION)
        raise typer.Exit()


# Command


@program.callback()
def program_main(
    version: Optional[bool] = typer.Option(None, "--version", callback=version)
):
    """Describe, extract, validate and transform tabular data."""
    pass
