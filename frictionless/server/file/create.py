from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ...project import Project
from ..router import router


class Result(BaseModel):
    path: str


@router.post("/file/create")
async def server_file_create(
    request: Request, file: UploadFile = File(), session: Optional[str] = Form()
) -> Result:
    project: Project = request.app.get_project(session)
    bytes = await file.read()
    path = project.file_create(file.filename, bytes=bytes)
    return Result(path=path)
