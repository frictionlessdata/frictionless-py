from __future__ import annotations

from fastapi import Request
from pydantic import BaseModel

from ...project import Project
from ...router import router

# TODO: implement


class Props(BaseModel):
    text: str


class Result(BaseModel):
    text: str


@router.post("/script/execute")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


def action(project: Project, props: Props) -> Result:
    return Result(text=props.text)
