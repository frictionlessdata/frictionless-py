from typer import Option as Opt
from ..system import system
from .main import program
from .. import settings


@program.command(name="api")
def program_api(
    port: int = Opt(settings.DEFAULT_SERVER_PORT, help="Specify server port"),
):
    """
    Start API server
    """
    server = system.create_server("api")
    server.start(port=port)
