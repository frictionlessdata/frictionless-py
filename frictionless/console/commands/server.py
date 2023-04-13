from __future__ import annotations
import typer
from ...platform import platform
from ..console import console
from .. import common


@console.command(name="server", hidden=True)
def console_server(
    folder: str = typer.Argument(default=None, help="Project folder [default: current]"),
    # Options
    port: int = common.port,
    debug: bool = common.debug,
):
    """
    Start Server
    """
    module = platform.frictionless_server
    config = module.Config.from_options(
        folder=folder,
        port=port,
        debug=debug,
    )
    server = module.Server.create(config)
    server.run()
