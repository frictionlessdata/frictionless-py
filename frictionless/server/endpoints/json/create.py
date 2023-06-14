from __future__ import annotations
from typing import Any
from fastapi import Request
from pydantic import BaseModel
from ...project import Project
from ...router import router
from ... import helpers


class Props(BaseModel):
    path: str
    data: Any


class Result(BaseModel):
    path: str


@router.post("/json/create")
def server_text_write(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    path = helpers.write_json(project, path=props.path, data=props.data)
    return Result(path=path)
