from __future__ import annotations
import typer
from ..resource import Resource
from ..system import system
from .program import program
from . import common


@program.command(name="index")
def program_index(
    source: str = common.source,
    database: str = common.database,
    table: str = common.table,
    fast: bool = common.fast,
    # Command
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Index a tabular data resource"""

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Index resource
    try:
        resource = Resource(source)
        resource.infer()
        resource.index(database_url=database, table_name=table, fast=fast)
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

    # Report result
    typer.secho(f'Indexed to "{database}/{table}"', bold=True)
    raise typer.Exit(0)
