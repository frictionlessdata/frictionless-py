from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ..project import Project
from ..router import router


class SessionsCreateFileProps(BaseModel):
    session: Optional[str]


@router.post("/project/create-file")
def server_file_create(
    request: Request, file: UploadFile = File(), data: SessionsCreateFileProps = Form()
):
    config = request.app.config
    project = Project(config, session=data.session)
    path = project.create_file(file)
    return {"path": path}
