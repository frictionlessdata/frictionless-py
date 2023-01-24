from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]


class Result(BaseModel):
    path: str


@router.post("/package/create")
def server_package_create(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    path = project.package_create()
    return Result(path=path)
