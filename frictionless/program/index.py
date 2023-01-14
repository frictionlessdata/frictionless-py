from __future__ import annotations
import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..resource import Resource
from ..system import system
from .program import program
from . import common
from .. import helpers


@program.command(name="index")
def program_index(
    source: str = common.source,
    database: str = common.database,
    table: str = common.table,
    fast: bool = common.fast,
    qsv: str = common.qsv,
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
        timer = helpers.Timer()
        resource = Resource(source)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            status = progress.add_task(description="Indexing...", total=None)
            callback = lambda msg: progress.update(status, description=f"Indexed {msg}")
            resource.index(
                database_url=database,
                table_name=table,
                fast=fast,
                qsv=qsv,
                callback=callback,
            )
        typer.secho(
            f"{progress.tasks[status].description} in {timer.time} seconds",
            bold=True,
        )
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise
