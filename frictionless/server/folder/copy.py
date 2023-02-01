from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    folder: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/folder/copy")
def server_folder_copy(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.folder_copy(props.path, folder=props.folder)
    return Result(path=path)
