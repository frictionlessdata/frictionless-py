import typer
from .main import program


@program.command(name="extract")
def program_extract():
    """
    Create a new user with USERNAME.
    """
    typer.echo("Exctract")
