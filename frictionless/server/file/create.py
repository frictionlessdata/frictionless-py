from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from fastapi import Request, UploadFile, File, Form
from ...project import Project
from ..router import router


class Result(BaseModel):
    path: str


@router.post("/file/create")
async def server_file_create(
    request: Request,
    file: UploadFile = File(),
    session: Optional[str] = Form(),
    folder: Optional[str] = Form(),
) -> Result:
    project: Project = request.app.get_project(session)
    path = file.filename
    if folder:
        path = str(Path(folder) / path)
    bytes = await file.read()
    project.file_create(path, bytes=bytes)
    return Result(path=path)
