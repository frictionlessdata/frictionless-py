from __future__ import annotations
import typer
from ..resource import Resource
from ..system import system
from .program import program
from . import common


@program.command(name="summary")
def program_summary(
    source: str = common.source,
    # Command
    debug: bool = common.debug,
    trusted: bool = common.trusted,
    standards: str = common.standards,
):
    """Summary of data source.

    It will return schema, sample of the data and validation report for the resource.
    """

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

    # Infer Resource
    try:
        resource = Resource(source)
        resource.infer()
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise
    typer.secho("")
    typer.secho("# Describe ", bold=True)
    typer.secho("")
    typer.secho(str(resource.schema.to_summary()))  # type: ignore
    typer.secho("")
    typer.secho("# Extract ", bold=True)
    typer.secho("")
    typer.secho(str(resource.to_view()))

    # Validate
    try:
        report = resource.validate()
    except Exception as exception:
        if not debug:
            typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
            raise typer.Exit(1)
        raise
    typer.secho("")
    typer.secho("# Validate ", bold=True)
    typer.secho(str(report.to_summary()))

    # Return retcode
    raise typer.Exit(code=int(not report.valid))
