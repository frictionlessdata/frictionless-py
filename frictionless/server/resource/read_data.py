from typing import Optional, Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ..router import router


class Props(BaseModel):
    session: Optional[str]
    path: str


class Result(BaseModel):
    data: Any


@router.post("/resource/read-data")
def server_resourec_read_data(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project(props.session)
    data = project.resource_read_data(props.path)
    return Result(data=data)
