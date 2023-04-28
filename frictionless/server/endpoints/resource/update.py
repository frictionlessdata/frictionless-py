from pydantic import BaseModel
from typing import Optional
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    resource: dict
    reindex: Optional[bool]


class Result(BaseModel):
    path: str


@router.post("/file/update")
def server_file_update(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    project.update_file(props.path, resource=props.resource, reindex=props.reindex)
    return Result(path=props.path)
