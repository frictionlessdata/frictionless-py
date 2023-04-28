from typing import Any
from pydantic import BaseModel
from fastapi import Request
from ....resources import JsonResource
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str


class Result(BaseModel):
    data: Any


@router.post("/json/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.path)
    resource = JsonResource(path=fullpath)
    data = resource.read_json()

    return Result(data=data)
