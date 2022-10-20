from __future__ import annotations
from ..platform import platform
from .config import Config
from .router import router
from .. import settings


# TODO: rebase on async endpoints
# TODO: review endpoints to use proper imports (use platform)


class Server(platform.fastapi.FastAPI):
    config: Config

    @staticmethod
    def create(config: Config):
        server = Server(
            title="Frictionless API",
            version=settings.VERSION,
            debug=config.debug,
        )
        server.config = config or Config()
        server.include_router(router)
        return server

    def run(self):
        log_level = "debug" if self.config.debug else None
        platform.uvicorn.run(
            self,
            port=self.config.port,
            log_level=log_level,
        )
