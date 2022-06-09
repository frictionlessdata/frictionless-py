from .server import server


@server.get("/extract")
def server_extract():
    return {"Hello": "World"}
