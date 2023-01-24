from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    bytes: bytes


@router.post("/file/read")
def server_file_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    bytes = project.file_read(props.path)
    return Result(bytes=bytes)
