from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    path: str


@router.post("/file/create-folder")
def server_file_create_folder(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.file_create_folder(props.path)
    return Result(path=path)
