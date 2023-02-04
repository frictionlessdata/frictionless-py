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


@router.post("/file/delete")
def server_file_delete(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.delete_file(props.path)
    return Result(path=props.path)
