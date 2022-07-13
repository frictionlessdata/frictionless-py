from __future__ import annotations
from .server import server


@server.get("/extract")
def server_extract():
    return {"Hello": "World"}
