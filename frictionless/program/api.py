from __future__ import annotations
from ..platform import platform
from .program import program
from . import common


@program.command(name="api")
def program_api(
    port: int = common.port,
):
    """
    Start API server
    """
    server = platform.frictionless_server.Server.create()
    platform.uvicorn.run(server, port=port)
