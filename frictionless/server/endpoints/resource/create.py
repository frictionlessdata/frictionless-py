from __future__ import annotations
from typing import Dict, Any
from pydantic import BaseModel
from fastapi import Request
from ....resource import Resource
from ...project import Project
from ...router import router


class Props(BaseModel, extra="forbid"):
    path: str


class Result(BaseModel, extra="forbid"):
    resource: Dict[str, Any]


@router.post("/resource/create")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    resource = Resource(path=props.path)
    return Result(resource=resource.to_descriptor())
