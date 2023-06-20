from __future__ import annotations

from typing import List

import typer
from rich.console import Console
from rich.progress import track
from rich.prompt import Prompt

from ...exception import FrictionlessException
from ...package import Package
from ...platform import platform
from ...resource import Resource
from ...system import system
from .. import common, helpers
from ..console import console


@console.command(name="publish")
def console_publish(
    # Resource
    source: List[str] = common.source,
    name: str = common.resource_name,
    type: str = common.type,
    path: str = common.path,
    # Command
    target: str = typer.Option(default=...),
    title: str = typer.Option(default=None),
    # System
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Script data"""
    console = Console()
    portals = platform.frictionless_portals

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

    try:
        # Get package
        resource = Resource(
            source=helpers.create_source(source),
            name=name,
            path=path,
            datatype=type,
        )
        resources = resource.list(name=name)
        package = Package(title=title, resources=resources)

        # Publish package
        console.rule("[bold]Publish")
        adapter = system.create_adapter(target, packagify=True)
        if not isinstance(adapter, portals.ckan.CkanAdapter):
            raise FrictionlessException("Currently only CKAN publishing is supported")
        apikey = Prompt.ask("Please enter [bold]API Key[/bold]")
        # TODO: replace dummy progress bar by the resource based (like for index)
        for stage in track(["start", "end"], description="Publishing..."):
            if stage == "end":
                package.publish(target, control=portals.ckan.CkanControl(apikey=apikey))

    except Exception as exception:
        helpers.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # Print result
    console.rule("[bold]Result")
    console.print(f"Succesefully published to [bold]{target}[/bold]")
