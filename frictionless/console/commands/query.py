from __future__ import annotations

import atexit
import os
import tempfile
from typing import List

import typer

from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console
from ..helpers import output_console


@console.command(name="query")
def console_query(
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

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = helpers.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        helpers.print_error(note=note)
        raise typer.Exit(code=1)

    # Index resource
    output_console.rule("[bold]Index")
    try:
        # Create resource
        resource = Resource(
            source=helpers.create_source(source),
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
                helpers.index_resource(
                    resource=resource,
                    database=database,
                    fast=True,
                    use_fallback=True,
                    debug=debug,
                )
            )
    except Exception as exception:
        helpers.print_exception(debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Ensure tables
    if not names:
        note = "Not found any tabular resources"
        helpers.print_error(note=note)
        raise typer.Exit(1)

    # Enter database
    output_console.rule("[bold]Query")
    os.system(f"sqlite3 {database}")
