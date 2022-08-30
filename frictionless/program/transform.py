from __future__ import annotations
import sys
import typer
from typing import List
from ..pipeline import Pipeline, Step
from ..actions import transform
from ..system import system
from .program import program
from .. import helpers
from . import common


@program.command(name="transform")
def program_transform(
    # Source
    source: List[str] = common.source,
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

    # Setup system
    if trusted:
        system.trusted = trusted
    if standards:
        system.standards = standards  # type: ignore

    # Support stdin
    is_stdin = False
    if not source:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]  # type: ignore

    # TODO: implement
    assert not is_stdin

    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Prepare source
    def prepare_source():
        return list(source) if len(source) > 1 else (source[0] if source else None)

    # Prepare pipeline
    def prepare_pipeline():
        descriptor = helpers.parse_json_string(pipeline)
        if descriptor:
            return Pipeline.from_descriptor(descriptor)
        step_objects = []
        for step_descriptor in helpers.parse_descriptors_string(steps) or []:
            step_objects.append(Step.from_descriptor(step_descriptor))
        return Pipeline.from_options(
            steps=step_objects,
        )

    # Prepare options
    def prepare_options():
        return dict(pipeline=prepare_pipeline())

    # Transform source
    try:
        resource = transform(prepare_source(), **prepare_options())
    # TODO: we don't catch errors here because it's streaming
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise

    # TODO: support outputing packages

    # Return default
    table = resource.to_petl()  # type: ignore
    schema = resource.schema.to_summary()  # type: ignore
    typer.secho("\n## Schema\n")
    typer.secho(schema)
    typer.secho("\n## Table\n")
    typer.secho(table)
