from __future__ import annotations

from typing import Any, Dict

from fastapi import Request
from pydantic import BaseModel

from ....dialect import Control
from ....package import Package
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str
    # TODO: use IControl?
    control: Dict[str, Any]


class Result(BaseModel, extra="forbid"):
    url: str


@router.post("/package/publish")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    fs = project.filesystem

    fullpath = fs.get_fullpath(props.path)
    package = Package.from_descriptor(str(fullpath))
    url = package.publish(control=Control.from_descriptor(props.control))

    return Result(url=url)
