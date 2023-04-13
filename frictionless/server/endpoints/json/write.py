from typing import Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    data: Any


class Result(BaseModel):
    path: str


@router.post("/json/write")
def server_json_read(request: Request, props: Props) -> Result:
    project: Project = request.app.get_project()
    project.write_json(props.path, data=props.data)
    return Result(path=props.path)
