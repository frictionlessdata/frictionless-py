from typing import Optional, Dict
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    record: Dict


@router.post("/resource/create")
def server_resource_create(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    record = project.resource_create(props.path)
    # TODO: fix types
    return Result(record=record)  # type: ignore
