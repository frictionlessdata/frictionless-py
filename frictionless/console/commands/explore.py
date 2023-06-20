from __future__ import annotations

import os
from typing import List

import typer
from rich.console import Console

from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console


@console.command(name="explore")
def console_explore(
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
    """Explore dataset with Visidata

    Please read the commands reference:
    - https://www.visidata.org/man/
    """
    console = Console()

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Create source
    source = helpers.create_source(source, path=path)
    if not source and not path:
        note = 'Providing "source" or "path" is required'
        helpers.print_error(console, note=note)
        raise typer.Exit(code=1)

    # Get paths
    try:
        resource = Resource(
            source=helpers.create_source(source),
            name=name,
            path=path,
            datatype=type,
        )
        resources = resource.list(name=name)
        paths = [resource.normpath for resource in resources if resource.normpath]
    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Enter editor
    os.system(f"vd {' '.join(paths)}")
