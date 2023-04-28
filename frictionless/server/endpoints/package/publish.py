from typing import Any, Dict
from pydantic import BaseModel
from fastapi import Request
from ....dialect import Control
from ....package import Package
from ...project import Project
from ...router import router


class Props(BaseModel):
    path: str
    # TODO: use IControl?
    control: Dict[str, Any]


class Result(BaseModel):
    path: str


@router.post("/package/publish")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.path)
    package = Package.from_descriptor(fullpath)
    path = package.publish(control=Control.from_descriptor(props.control))

    return Result(path=path)
