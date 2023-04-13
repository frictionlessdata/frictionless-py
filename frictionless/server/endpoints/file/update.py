from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    session: Optional[str]
    path: str
    resource: dict


class Result(BaseModel):
    path: str


@router.post("/file/update")
def server_file_update(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    project.update_file(props.path, resource=props.resource)
    return Result(path=props.path)
