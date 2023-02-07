from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ...project import Project, IFile
from ..router import router


# See the signature
class Props(BaseModel):
    pass


class Result(BaseModel):
    file: IFile


@router.post("/file/create")
async def server_file_create(
    request: Request,
    file: UploadFile = File(),
    folder: Optional[str] = Form(None),
    session: Optional[str] = Form(None),
) -> Result:
    project: Project = request.app.get_project(session)
    name = file.filename
    bytes = await file.read()
    resfile = project.create_file(name, bytes=bytes, folder=folder)
    return Result(file=resfile)
