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
    from ..server import server

    platform.uvicorn.run(server, port=port)  # type: ignore
