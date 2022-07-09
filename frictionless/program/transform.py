# type: ignore
import sys
import typer
from ..pipeline import Pipeline
from ..actions import transform
from .main import program
from . import common


@program.command(name="transform")
def program_transform(
    # Source
    source: str = common.source,
    # Pipeline
    pipeline: str = common.pipeline,
    # Command
    yaml: bool = common.yaml,
    json: bool = common.json,
    debug: bool = common.debug,
):
    """Transform data using a provided pipeline.

    Please read more about Transform pipelines to write a pipeline
    that can be accepted by this function.
    """

    # Support stdin
    is_stdin = False
    if not source:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]

    # TODO: implement
    assert not is_stdin

    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # TODO: it's a dummy implemenation (we need a proper one)
    # TODO: support for a package
    # Transform source
    try:
        pipeline = Pipeline(pipeline)
        resource = transform(source, pipeline=pipeline)
        typer.secho("")
        typer.secho(resource.to_petl())
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise
