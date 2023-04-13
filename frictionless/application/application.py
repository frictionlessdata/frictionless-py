from __future__ import annotations
from pathlib import Path
from ..platform import platform
from .config import Config
from .. import settings
from .. import server


class Application(platform.fastapi.FastAPI):
    config: Config

    @staticmethod
    def create(config: Config):
        application = Application(
            title="Frictionless Application",
            version=settings.VERSION,
            debug=config.debug,
        )
        application.config = config or Config()

        # Mount server/client
        application.mount("/api", server.Server.create(config))
        application.mount(
            "/",
            platform.fastapi_staticfiles.StaticFiles(
                directory=Path(__file__).parent / "client",
                html=True,
            ),
            name="client",
        )

        return application

    # Run

    def run(self):
        log_level = "debug" if self.config.debug else None
        platform.uvicorn.run(
            self,
            port=self.config.port,
            log_level=log_level,
        )
