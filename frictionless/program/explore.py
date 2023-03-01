from __future__ import annotations
import os
import atexit
import typer
import tempfile
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..resource import Resource
from ..package import Package
from .program import program
from .. import helpers
from . import common


@program.command(name="explore")
def program_explore(
    source: str = typer.Argument(default=None),
    # Options
    sql: bool = typer.Option(default=False),
    debug: bool = common.debug,
):
    """Explore a data resource or package"""
    resource = Resource(path=source)

    # Create database
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    atexit.register(os.remove, file.name)
    database_path = file.name

    # Populate database
    try:
        package = Package(source)
        for resource in package.resources:
            index_resource(resource, database_path=database_path, debug=debug)
    except Exception:
        resource = Resource(source)
        if resource.type != "table":
            note = f"Not suported data type: {resource.datatype}"
            typer.secho(note, err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        index_resource(resource, database_path=database_path, debug=debug)

    # Sql
    if sql:
        os.system(f"sqlite3 {database_path}")
        raise typer.Exit()


# Internal


def index_resource(resource: Resource, *, database_path: str, debug: bool = False):
    try:
        timer = helpers.Timer()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            redirect_stdout=not debug,
            redirect_stderr=not debug,
            transient=True,
        ) as progress:
            status = progress.add_task(
                description=f"[{resource.name}] Indexing...", total=None
            )
            on_progress = lambda m: progress.update(
                status, description=f"[{resource.name}] Indexed {m}"
            )
            resource.index(
                database_url=f"sqlite:////{database_path}",
                table_name=resource.name,
                fast=True,
                use_fallback=True,
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
