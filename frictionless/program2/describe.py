import typer
from .main import program


@program.command(name="describe")
def program_describe():
    """
    Create a new user with USERNAME.
    """
    typer.echo("Describe")
