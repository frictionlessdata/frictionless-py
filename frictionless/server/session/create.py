from __future__ import annotations
import secrets
from ..server import server


@server.post("/session/create")
def server_session_create():
    return dict(token=secrets.token_urlsafe(16))
