from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from .. import settings
from ..platform import platform
from .config import Config
from .project import Project
from .router import router

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

        @server.exception_handler(Exception)  # type: ignore
        async def exception_handler(request: Request, exception: Exception):  # type: ignore
            return JSONResponse(
                status_code=400,
                content={"detail": str(exception)},
            )

        server.config = config or Config()
        server.include_router(router)  # type: ignore
        return server

    # Run

    def run(self):
        log_level = "debug" if self.config.debug else None
        platform.uvicorn.run(  # type: ignore
            self,
            workers=1,
            port=self.config.port,
            log_level=log_level,
        )

    # Context

    def get_project(self):
        return Project(self.config.folder)
