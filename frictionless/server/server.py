from __future__ import annotations
from ..platform import platform
from .. import settings


server = platform.fastapi.FastAPI(title="Frictionless API", version=settings.VERSION)
