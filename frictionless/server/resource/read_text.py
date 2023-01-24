from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    contents: str


@router.post("/file/read-text")
def server_resource_read_text(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    contents = project.resource_read_text(props.path)
    return Result(contents=contents)
