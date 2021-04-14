import sys
import typer
from ..transform import transform
from .main import program
from . import common


@program.command(name="transform")
def program_transform(
    # Source
    source: str = common.source,
):
    """Transform data using a provided pipeline.

    Please read more about Transform pipelines to write a pipeline
    that can be accepted by this funtion.
    """

    # Support stdin
    is_stdin = False
    if not source:
        is_stdin = True
        source = [sys.stdin.buffer.read()]

    # Transform source
    try:
        transform(source)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return default
    if is_stdin:
        source = "stdin"
    prefix = "success"
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho(f"# {prefix}: {source}", bold=True)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
