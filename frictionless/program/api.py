import click
from .main import program
from ..system import system
from .. import config


@program.command(name="api")
@click.option("--port", type=int, default=config.DEFAULT_SERVER_PORT, help="Server port")
def program_api(port):
    """Start API
    \f
    API      | Usage
    -------- | --------
    Public   | `$ frictionless api`
    """
    server = system.create_server("api")
    server.listen(port=port)
