from pydantic import BaseModel
from fastapi import Request
from ..session import Session
from ..router import router


class SessionsDeleteFileProps(BaseModel):
    token: str
    path: str


@router.post("/session/delete-file")
def server_file_create(request: Request, props: SessionsDeleteFileProps):
    config = request.app.config
    session = Session(config, token=props.token)
    path = session.delete_file(props.path)
    return {"path": path}
