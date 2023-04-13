from __future__ import annotations
from ...platform import platform
from ..console import console
from .. import common


@console.command(name="server", hidden=True)
def console_server(
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
        is_root=root,
        port=port,
        debug=debug,
    )
    server = module.Server.create(config)
    server.run()
