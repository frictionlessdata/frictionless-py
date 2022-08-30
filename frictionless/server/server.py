from __future__ import annotations
from ..platform import platform
from .config import ServerConfig
from .. import settings


# TODO: review endpoints to use proper imports (use platform)


class Server(platform.fastapi.FastAPI):
    config: ServerConfig


server = Server(title="Frictionless API", version=settings.VERSION)
server.config = ServerConfig()
