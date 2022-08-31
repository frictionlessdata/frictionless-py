from __future__ import annotations
from fastapi import Request
from ..session import Session
from ..router import router


# TODO: protect against many sessions creation


@router.post("/session/create")
def server_session_create(request: Request):
    config = request.app.config
    session = Session(config)
    return dict(token=session.token)
