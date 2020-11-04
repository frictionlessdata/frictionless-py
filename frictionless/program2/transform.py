import typer
from .main import program


@program.command(name="transform")
def program_transform():
    """
    Create a new user with USERNAME.
    """
    typer.echo("Transform")
