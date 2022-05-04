from ...plugin import Plugin
from .server import ApiServer


# TODO: Rename to ApiPlugin


# Plugin


class ServerPlugin(Plugin):
    """Plugin for Server

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.server import ServerPlugin`

    """

    code = "server"
    status = "experimental"

    def create_server(self, name):
        if name == "api":
            return ApiServer()
