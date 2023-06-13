from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel):
    path: str


class Result(BaseModel):
    data: Any


@router.post("/json/read")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    data = helpers.read_json(project, path=props.path)
    return Result(data=data)
