from __future__ import annotations
from typing import Optional
from ..platform import platform
from .config import Config
from .router import router
from .. import settings


# TODO: rebase on async endpoints
# TODO: review endpoints to use proper imports (use platform)


class Server(platform.fastapi.FastAPI):
    config: Config

    @staticmethod
    def create(config: Optional[Config] = None):
        server = Server(title="Frictionless API", version=settings.VERSION)
        server.config = config or Config()
        server.include_router(router)
        return server
