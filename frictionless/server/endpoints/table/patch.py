from __future__ import annotations
from pydantic import BaseModel
from fastapi import Request
from ...project import Project
from ...router import router
from ... import models


class Props(BaseModel):
    path: str
    history: models.History


class Result(BaseModel):
    path: str


@router.post("/table/patch")
def endpoint(request: Request, props: Props) -> Result:
    return action(request.app.get_project(), props)


# TODO: implement
def action(project: Project, props: Props) -> Result:
    fs = project.filesystem
    db = project.database

    print(fs)
    print(db)

    return Result(path=props.path)
