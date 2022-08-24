from __future__ import annotations
from .server import server


@server.get("/describe")
def server_describe():
    return {"Hello": "World"}
