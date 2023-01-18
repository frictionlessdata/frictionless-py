from __future__ import annotations
from typing import Optional
from ..platform import platform
from ..project import Project
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

    # Server

    def run(self):
        log_level = "debug" if self.config.debug else None
        platform.uvicorn.run(
            self,
            port=self.config.port,
            log_level=log_level,
        )

    # Project

    def get_project(self, session: Optional[str]):
        return Project(
            session=session,
            basepath=self.config.basepath,
            is_root=self.config.is_root,
        )
