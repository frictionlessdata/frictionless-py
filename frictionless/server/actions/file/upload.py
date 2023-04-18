from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ...project import Project
from ...router import router


# See the signature
class Props(BaseModel):
    pass


class Result(BaseModel):
    path: str


# TODO: merge into write?
@router.post("/file/upload")
async def server_file_upload(
    request: Request,
    file: UploadFile = File(),
    folder: Optional[str] = Form(None),
) -> Result:
    project: Project = request.app.get_project()
    name = file.filename or "name"
    bytes = await file.read()
    path = project.upload_file(name, bytes=bytes, folder=folder)
    return Result(path=path)
