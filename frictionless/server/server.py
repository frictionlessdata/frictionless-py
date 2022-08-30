from __future__ import annotations
from ..platform import platform


# TODO: split on validate/resource|package|inquiry|etc


server = platform.fastapi.FastAPI(title="Frictionless API")
