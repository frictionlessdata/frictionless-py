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
    fallback: bool = common.fallback,
    metadata: bool = common.metadata,
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

    # Prepare database url
    if "://" not in database:
        database = f"sqlite:///{database}"

    # Index resource
    try:
        timer = helpers.Timer()
        resource = Resource(source)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            redirect_stdout=not debug,
            redirect_stderr=not debug,
            transient=True,
        ) as progress:
            status = progress.add_task(description="Indexing...", total=None)
            on_progress = lambda m: progress.update(status, description=f"Indexed {m}")
            resource.index(
                database_url=database,
                table_name=table,
                fast=fast,
                qsv_path=qsv,
                use_fallback=fallback,
                with_metadata=metadata,
                on_progress=on_progress,
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
