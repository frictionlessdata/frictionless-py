from __future__ import annotations
import typer
from typing import List
from rich.console import Console
from ...exception import FrictionlessException
from ...platform import platform
from ...resource import Resource
from ...system import system
from ..console import console
from .. import common
from .. import utils


@console.command(name="transform", hidden=True)
def console_transform(
    # Source
    source: List[str] = common.source,
    path: str = common.path,
    # Pipeline
    pipeline: str = common.pipeline,
    steps: str = common.steps,
    # Command
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Transform data using a provided pipeline.

    Please read more about Transform pipelines to write a pipeline
    that can be accepted by this function.
    """
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

    # Create pipeline
    pipeline_obj = utils.create_pipeline(
        descriptor=pipeline,
        steps=steps,
    )

    # Transform resource
    try:
        resource = Resource(source, path=path)
        if not isinstance(resource, platform.frictionless_resources.Transformable):
            note = f'Resource with data type "{resource.datatype}" is not transformable'
            raise FrictionlessException(note)
        result = resource.transform(pipeline_obj)
    # TODO: we don't catch errors here because it's streaming
    except Exception as exception:
        utils.print_exception(console, debug=debug, exception=exception)
        raise typer.Exit(code=1)

    # TODO: support outputing packages

    # Return default
    table = result.to_petl()  # type: ignore
    schema = result.schema.to_summary()  # type: ignore
    typer.secho("\n## Schema\n")
    typer.secho(schema)
    typer.secho("\n## Table\n")
    typer.secho(table)
