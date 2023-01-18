from typing import Optional
from fastapi import Request, UploadFile, File, Form
from ..router import router


@router.post("/project/create-file")
def server_create_file(
    request: Request, file: UploadFile = File(), session: Optional[str] = Form()
):
    project = request.app.get_project(session)
    path = project.create_file(file)
    return {"path": path}
