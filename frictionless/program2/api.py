import typer
from .main import program


@program.command(name="api")
def program_api():
    """
    Create a new user with USERNAME.
    """
    typer.echo("API")
