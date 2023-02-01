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


@router.post("/folder/delete")
def server_folder_delete(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.folder_delete(props.path)
    return Result(path=props.path)
