import typer
from .main import program


@program.command(name="validate")
def program_validate():
    """
    Create a new user with USERNAME.
    """
    typer.echo("Validate")
