from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IFile
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    file: IFile


@router.post("/resource/provide")
def server_resource_provide(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    file = project.provide_resource(props.path)
    return Result(file=file)
