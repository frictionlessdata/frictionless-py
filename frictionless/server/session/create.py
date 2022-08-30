from __future__ import annotations
import secrets
from ..router import router


@router.post("/session/create")
def server_session_create():
    return dict(token=secrets.token_urlsafe(16))
