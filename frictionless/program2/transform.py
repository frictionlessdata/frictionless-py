import typer
from ..transform import transform
from typer import Argument as Arg
from .main import program


@program.command(name="transform")
def program_transform(
    source: str = Arg(..., help="Path to a transform pipeline"),
):
    """Transform data source using a provided pipeline."""

    # Transform source
    try:
        transform(source)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return default
    typer.secho(f'[success] pipeline "{source}"', bold=True, fg=typer.colors.GREEN)
