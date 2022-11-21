from typing import Optional
from fastapi import Request, UploadFile, File, Form
from ..project import Project
from ..router import router


@router.post("/project/create-file")
def server_create_file(
    request: Request, file: UploadFile = File(), session: Optional[str] = Form()
):
    config = request.app.config
    project = Project(config, session=session)
    path = project.create_file(file)
    return {"path": path}
