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


@router.post("/file/copy")
def server_file_copy(request: Request, props: Props) -> Result:
    # TODO: why do we need to provide type explicetly?
    project: Project = request.app.get_project(props.session)
    path = project.copy_file(props.path, folder=props.folder)
    return Result(path=path)
