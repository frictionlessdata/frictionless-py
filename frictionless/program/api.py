from __future__ import annotations
from ..platform import platform
from .program import program
from . import common


@program.command(name="api")
def program_api(
    basepath: str = common.basepath,
    root: bool = common.root,
    port: int = common.port,
    debug: bool = common.debug,
):
    """
    Start API server
    """
    module = platform.frictionless_server
    config = module.Config.from_options(
        basepath=basepath,
        root=root,
        port=port,
        debug=debug,
    )
    server = module.Server.create(config)
    server.run()
