from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ..session import Session
from ..router import router


class SessionListFilesProps(BaseModel):
    token: Optional[str]


@router.post("/session/list-files")
def server_file_create(request: Request, props: SessionListFilesProps):
    config = request.app.config
    session = Session(config, token=props.token)
    paths = session.list_files()
    return {"paths": paths}
