from typing import Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    data: Any


@router.post("/json/read")
def server_json_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    data = project.read_json(props.path)
    return Result(data=data)
