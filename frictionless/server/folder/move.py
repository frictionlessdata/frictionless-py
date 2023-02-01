from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    folder: str


class Result(BaseModel):
    path: str


@router.post("/folder/move")
def server_folder_move(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.folder_move(props.path, folder=props.folder)
    return Result(path=path)
