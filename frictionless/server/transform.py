from __future__ import annotations
from .server import server


@server.get("/transform")
def server_transform():
    return {"Hello": "World"}
