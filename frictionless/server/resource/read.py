from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from ...project import Project, IRecord
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    record: Optional[IRecord]


@router.post("/resource/read")
def server_resource_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    record = project.resource_read(props.path)
    return Result(record=record)
