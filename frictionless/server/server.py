from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from ..platform import platform
from .project import Project
from .config import Config
from .router import router
from .. import settings


# TODO: handle errors
# TODO: rebase on async endpoints
# TODO: review endpoints to use proper imports (use platform)


class Server(platform.fastapi.FastAPI):
    config: Config

    @staticmethod
    def create(config: Config):
        server = Server(
            title="Frictionless Server",
            version=settings.VERSION,
            debug=config.debug,
        )

        @server.exception_handler(Exception)
        async def exception_handler(request: Request, exception: Exception):  # type: ignore
            return JSONResponse(
                status_code=400,
                content={"detail": str(exception)},
            )

        server.config = config or Config()
        server.include_router(router)
        return server

    # Run

    def run(self):
        log_level = "debug" if self.config.debug else None
        platform.uvicorn.run(  # type: ignore
            self,
            port=self.config.port,
            log_level=log_level,
        )

    # Context

    def get_project(self):
        return Project(self.config.folder)
