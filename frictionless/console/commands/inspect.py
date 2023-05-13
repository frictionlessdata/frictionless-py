from __future__ import annotations
import os
import atexit
import typer
import tempfile
from typing import List
from rich.console import Console
from ...resource import Resource
from ..console import console
from ...system import system
from .. import common
from .. import utils


# TODO: figure out how we can reduce duplication among commands like this: query/etc
@console.command(name="inspect", hidden=True)
def console_inspect(
    # Resource
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Query data"""
    console = Console()

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = utils.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        utils.print_error(console, note=note)
        raise typer.Exit(code=1)

    # Index resource
    console.rule("[bold]Index")
    try:
        # Create resource
        resource = Resource(
            source=utils.create_source(source),
            name=name,
            path=path,
            datatype=type,
        )

        # Create database
        file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        atexit.register(os.remove, file.name)
        database = file.name

        # Index resources
        names: List[str] = []
        resources = resource.list(name=name)
        for resource in resources:
            names.extend(
                utils.index_resource(
                    console,
                    resource=resource,
                    database=database,
                    fast=True,
                    use_fallback=True,
                    debug=debug,
                )
            )
    except Exception as exception:
        utils.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Ensure tables
    if not names:
        note = "Not found any tabular resources"
        utils.print_error(console, note=note)
        raise typer.Exit(1)

    # Enter database
    console.rule("[bold]Inspect")
    os.system(f"datasette {database}")
