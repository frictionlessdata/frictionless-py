from __future__ import annotations
import os
import atexit
import typer
import tempfile
from typing import List
from rich.progress import Progress, SpinnerColumn, TextColumn
from ..resources import TableResource, PackageResource
from ..resource import Resource
from .program import program
from .. import helpers
from . import common


@program.command(name="query")
def program_query(
    source: str = typer.Argument(default=None),
    # Options
    debug: bool = common.debug,
):
    """Query data"""

    # Get tabular resources
    try:
        resources: List[TableResource] = []
        resource = Resource(source)
        if isinstance(resource, PackageResource):
            package = resource.read_package()
            for resource in package.resources:
                if isinstance(resource, TableResource):
                    resources.append(resource)
        elif isinstance(resource, TableResource):
            resources.append(resource)
    except Exception as exception:
        if debug:
            raise
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Ensure tabular resources
    if not resources:
        note = "Not found any tabular resources"
        typer.secho(note, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Index resources
    tables: List[str] = []
    file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    atexit.register(os.remove, file.name)
    database_path = file.name
    for resource in resources:
        result = index_resource(resource, database_path=database_path, debug=debug)
        if result:
            tables.append(resource.name)

    # Ensure tables
    if not tables:
        note = "Not indexed any tabular resources"
        typer.secho(note, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Enter database
    os.system(f"sqlite3 {database_path}")
    raise typer.Exit()


# Internal


def index_resource(
    resource: TableResource, *, database_path: str, debug: bool = False
) -> bool:
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
                description=f"({resource.name}) Indexing...", total=None
            )
            on_progress = lambda m: progress.update(
                status, description=f"({resource.name}) Indexed {m}"
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
        return True
    except Exception:
        if debug:
            raise
        typer.secho(f"({resource.name}) errored", bold=True)
        return False
