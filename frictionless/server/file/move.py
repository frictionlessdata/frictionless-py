from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    source: str
    target: str


class Result(BaseModel):
    path: str


@router.post("/file/move")
def server_file_move(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.file_move(props.source, props.target)
    return Result(path=props.target)
