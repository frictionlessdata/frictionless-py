from typing import Optional
from fastapi import Request, UploadFile, File, Form
from ..session import Session
from ..router import router


@router.post("/session/create-file")
def server_file_create(
    request: Request, file: UploadFile = File(), token: Optional[str] = Form()
):
    config = request.app.config
    session = Session(config, token=token)
    path = session.create_file(file)
    return {"path": path}
