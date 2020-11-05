import typer
from typer import Option as Opt
from .main import program


@program.command(name="validate")
def program_validate(
    header_case: bool = Opt(True, help="Whether to ignore the case in validation"),
):
    """
    Create a new user with USERNAME.
    """
    typer.echo("Validate")
