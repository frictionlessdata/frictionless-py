from pydantic import BaseModel
from fastapi import Request, UploadFile
from ..session import Session
from ..router import router


class SessionCreateFileProps(BaseModel):
    token: str


@router.post("/session/create-file")
def server_file_create(request: Request, file: UploadFile, props: SessionCreateFileProps):
    config = request.app.config
    session = Session(config, token=props.token)
    path = session.create_file(file)
    return {"path": path}
