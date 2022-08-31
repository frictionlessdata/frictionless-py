from __future__ import annotations
from fastapi import Request
from ..router import router


# TODO: protect against many sessions creation


@router.post("/session/create")
def server_session_create(request: Request):
    token = request.app.state.create_session()
    return dict(token=token)
