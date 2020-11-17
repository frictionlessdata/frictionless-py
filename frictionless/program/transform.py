import sys
import typer
from ..transform import transform
from typer import Argument as Arg
from .main import program
from .. import helpers


@program.command(name="transform")
def program_transform(
    source: str = Arg(None, help="Path to a transform pipeline [default: stdin]"),
):
    """Transform data source using a provided pipeline."""

    # Support stdin
    is_stdin = False
    if not source:
        is_stdin = True
        source = [helpers.create_byte_stream(sys.stdin.buffer.read())]

    # Transform source
    try:
        transform(source)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return default
    if is_stdin:
        source = "stdin"
    typer.secho("---")
    typer.secho(f'success: "{source}"', bold=True)
    typer.secho("---")
